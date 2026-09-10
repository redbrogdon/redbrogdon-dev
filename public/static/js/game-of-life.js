/**
 * Subtle Ambient Conway's Game of Life Background
 * Implemented via WebGL ping-pong fragment shaders.
 */
(function () {
  'use strict';

  // Configuration
  const CELL_SIZE = 22;             // Cell size in CSS pixels
  const STEP_INTERVAL = 1800;       // Duration of a full generation cycle in ms
  const TRANSITION_DURATION = 900;  // Duration of smooth cross-fade between generations in ms
  const INITIAL_DENSITY = 0.18;     // Probability of a cell starting alive
  const ENTROPY_INTERVAL = 24000;   // Inject small life pattern every ~24 seconds

  // Vertex shader for fullscreen quad
  const VS_SOURCE = `
    attribute vec2 a_position;
    void main() {
      gl_Position = vec4(a_position, 0.0, 1.0);
    }
  `;

  // Simulation fragment shader: computes Conway's rules into offscreen FBO
  const FS_SIM_SOURCE = `
    precision mediump float;
    uniform sampler2D u_state;
    uniform vec2 u_resolution;

    float getCell(vec2 offset) {
      // Offset + u_resolution ensures strictly positive coordinates for mod
      vec2 coord = mod(gl_FragCoord.xy + offset + u_resolution, u_resolution) / u_resolution;
      return texture2D(u_state, coord).r > 0.5 ? 1.0 : 0.0;
    }

    void main() {
      float current = getCell(vec2(0.0, 0.0));
      float neighbors =
        getCell(vec2(-1.0, -1.0)) + getCell(vec2(0.0, -1.0)) + getCell(vec2(1.0, -1.0)) +
        getCell(vec2(-1.0,  0.0))                             + getCell(vec2(1.0,  0.0)) +
        getCell(vec2(-1.0,  1.0)) + getCell(vec2(0.0,  1.0)) + getCell(vec2(1.0,  1.0));

      float next = 0.0;
      if (current > 0.5) {
        if (neighbors == 2.0 || neighbors == 3.0) {
          next = 1.0;
        }
      } else {
        if (neighbors == 3.0) {
          next = 1.0;
        }
      }

      // r: new generation state, g: previous generation state
      gl_FragColor = vec4(next, current, 0.0, 1.0);
    }
  `;

  // Display fragment shader: renders to canvas with smooth easing and color mapping
  const FS_DISPLAY_SOURCE = `
    precision mediump float;
    uniform sampler2D u_state;
    uniform vec2 u_gridResolution;
    uniform float u_cellPixelSize;
    uniform float u_transition;
    uniform vec3 u_colorBg;
    uniform vec3 u_colorCell;

    void main() {
      // Map physical fragment position to grid cell index
      vec2 cellIndex = floor(gl_FragCoord.xy / u_cellPixelSize);
      vec2 uv = (mod(cellIndex, u_gridResolution) + 0.5) / u_gridResolution;
      vec4 state = texture2D(u_state, uv);

      float curr = state.r;
      float prev = state.g;

      // Smooth cubic ease-in-out interpolation between generations
      float t = clamp(u_transition, 0.0, 1.0);
      float eased = t * t * (3.0 - 2.0 * t);
      float alive = mix(prev, curr, eased);

      // Subtle 1px margin between cells so life structures remain legible
      vec2 cellPixel = mod(gl_FragCoord.xy, u_cellPixelSize);
      if (cellPixel.x < 1.0 || cellPixel.y < 1.0) {
        alive = 0.0;
      }

      vec3 color = mix(u_colorBg, u_colorCell, alive);
      gl_FragColor = vec4(color, 1.0);
    }
  `;

  function parseCssColor(colorStr, defaultRgb) {
    if (!colorStr) return defaultRgb;
    colorStr = colorStr.trim();

    // Handle hex: #rgb, #rgba, #rrggbb, #rrggbbaa
    if (colorStr.startsWith('#')) {
      const hex = colorStr.slice(1);
      if (hex.length === 3 || hex.length === 4) {
        const r = parseInt(hex[0] + hex[0], 16) / 255;
        const g = parseInt(hex[1] + hex[1], 16) / 255;
        const b = parseInt(hex[2] + hex[2], 16) / 255;
        return [r, g, b];
      } else if (hex.length >= 6) {
        const r = parseInt(hex.slice(0, 2), 16) / 255;
        const g = parseInt(hex.slice(2, 4), 16) / 255;
        const b = parseInt(hex.slice(4, 6), 16) / 255;
        return [r, g, b];
      }
    }

    // Handle rgb(r, g, b) or rgba(r, g, b, a)
    const rgbMatch = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
    if (rgbMatch) {
      return [
        parseInt(rgbMatch[1], 10) / 255,
        parseInt(rgbMatch[2], 10) / 255,
        parseInt(rgbMatch[3], 10) / 255
      ];
    }

    return defaultRgb;
  }

  function createShader(gl, type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      console.warn('Shader compile error:', gl.getShaderInfoLog(shader));
      gl.deleteShader(shader);
      return null;
    }
    return shader;
  }

  function createProgram(gl, vsSource, fsSource) {
    const vs = createShader(gl, gl.VERTEX_SHADER, vsSource);
    const fs = createShader(gl, gl.FRAGMENT_SHADER, fsSource);
    if (!vs || !fs) return null;

    const program = gl.createProgram();
    gl.attachShader(program, vs);
    gl.attachShader(program, fs);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.warn('Program link error:', gl.getProgramInfoLog(program));
      gl.deleteProgram(program);
      return null;
    }
    return program;
  }

  function createTexture(gl, width, height, data) {
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texImage2D(
      gl.TEXTURE_2D,
      0,
      gl.RGBA,
      width,
      height,
      0,
      gl.RGBA,
      gl.UNSIGNED_BYTE,
      data
    );
    return texture;
  }

  function createFBO(gl, texture) {
    const fbo = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
    gl.framebufferTexture2D(
      gl.FRAMEBUFFER,
      gl.COLOR_ATTACHMENT0,
      gl.TEXTURE_2D,
      texture,
      0
    );
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    return fbo;
  }

  function initGameOfLife() {
    let canvas = document.getElementById('game-of-life-canvas');
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = 'game-of-life-canvas';
      document.body.prepend(canvas);
    }

    const gl = canvas.getContext('webgl', {
      alpha: false,
      depth: false,
      stencil: false,
      antialias: false,
      preserveDrawingBuffer: false
    }) || canvas.getContext('experimental-webgl');

    if (!gl) return;

    // Fullscreen quad buffer
    const quadBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer);
    gl.bufferData(
      gl.ARRAY_BUFFER,
      new Float32Array([
        -1.0, -1.0,
         1.0, -1.0,
        -1.0,  1.0,
        -1.0,  1.0,
         1.0, -1.0,
         1.0,  1.0
      ]),
      gl.STATIC_DRAW
    );

    // Programs
    const simProgram = createProgram(gl, VS_SOURCE, FS_SIM_SOURCE);
    const displayProgram = createProgram(gl, VS_SOURCE, FS_DISPLAY_SOURCE);
    if (!simProgram || !displayProgram) return;

    // Simulation locations
    const simPosLoc = gl.getAttribLocation(simProgram, 'a_position');
    const simStateLoc = gl.getUniformLocation(simProgram, 'u_state');
    const simResLoc = gl.getUniformLocation(simProgram, 'u_resolution');

    // Display locations
    const dispPosLoc = gl.getAttribLocation(displayProgram, 'a_position');
    const dispStateLoc = gl.getUniformLocation(displayProgram, 'u_state');
    const dispGridResLoc = gl.getUniformLocation(displayProgram, 'u_gridResolution');
    const dispCellPixelLoc = gl.getUniformLocation(displayProgram, 'u_cellPixelSize');
    const dispTransLoc = gl.getUniformLocation(displayProgram, 'u_transition');
    const dispColorBgLoc = gl.getUniformLocation(displayProgram, 'u_colorBg');
    const dispColorCellLoc = gl.getUniformLocation(displayProgram, 'u_colorCell');

    let gridWidth = 0;
    let gridHeight = 0;
    let cellPixelSize = CELL_SIZE;
    let textures = [null, null];
    let fbos = [null, null];
    let currentIdx = 0; // Current state texture index

    let colorBg = [0.984, 0.976, 0.957];
    let colorCell = [0.969, 0.961, 0.937];

    function updateThemeColors() {
      const styles = getComputedStyle(document.documentElement);
      const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      const defaultBg = isDark ? [0.082, 0.078, 0.074] : [0.984, 0.976, 0.957];
      const defaultCell = isDark ? [0.114, 0.106, 0.098] : [0.969, 0.961, 0.937];

      colorBg = parseCssColor(styles.getPropertyValue('--bg'), defaultBg);
      colorCell = parseCssColor(styles.getPropertyValue('--bg-cell'), defaultCell);
    }

    function generateSeedData(width, height) {
      const size = width * height * 4;
      const data = new Uint8Array(size);
      for (let i = 0; i < width * height; i++) {
        const alive = Math.random() < INITIAL_DENSITY ? 255 : 0;
        data[i * 4] = alive;     // r: current
        data[i * 4 + 1] = alive; // g: previous
        data[i * 4 + 2] = 0;
        data[i * 4 + 3] = 255;
      }
      return data;
    }

    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const displayWidth = window.innerWidth;
      const displayHeight = window.innerHeight;

      canvas.width = Math.floor(displayWidth * dpr);
      canvas.height = Math.floor(displayHeight * dpr);

      cellPixelSize = CELL_SIZE * dpr;

      const newGridWidth = Math.max(16, Math.ceil(canvas.width / cellPixelSize));
      const newGridHeight = Math.max(16, Math.ceil(canvas.height / cellPixelSize));

      if (newGridWidth !== gridWidth || newGridHeight !== gridHeight) {
        gridWidth = newGridWidth;
        gridHeight = newGridHeight;

        // Clean up previous resources
        for (let i = 0; i < 2; i++) {
          if (textures[i]) gl.deleteTexture(textures[i]);
          if (fbos[i]) gl.deleteFramebuffer(fbos[i]);
        }

        const seedData = generateSeedData(gridWidth, gridHeight);
        textures[0] = createTexture(gl, gridWidth, gridHeight, seedData);
        textures[1] = createTexture(gl, gridWidth, gridHeight, seedData);
        fbos[0] = createFBO(gl, textures[0]);
        fbos[1] = createFBO(gl, textures[1]);
        currentIdx = 0;
      }

      updateThemeColors();
    }

    function injectEntropy() {
      if (!gridWidth || !gridHeight) return;
      // Inject an R-pentomino at a random location
      const pattern = [
        [0, 1, 1],
        [1, 1, 0],
        [0, 1, 0]
      ];
      const startX = Math.floor(Math.random() * (gridWidth - 4));
      const startY = Math.floor(Math.random() * (gridHeight - 4));
      const patch = new Uint8Array(3 * 3 * 4);

      for (let y = 0; y < 3; y++) {
        for (let x = 0; x < 3; x++) {
          const idx = (y * 3 + x) * 4;
          const alive = pattern[y][x] ? 255 : 0;
          patch[idx] = alive;
          patch[idx + 1] = alive;
          patch[idx + 2] = 0;
          patch[idx + 3] = 255;
        }
      }

      gl.bindTexture(gl.TEXTURE_2D, textures[currentIdx]);
      gl.texSubImage2D(
        gl.TEXTURE_2D,
        0,
        startX,
        startY,
        3,
        3,
        gl.RGBA,
        gl.UNSIGNED_BYTE,
        patch
      );
    }

    function stepSimulation() {
      const nextIdx = 1 - currentIdx;

      // Render simulation into next FBO
      gl.bindFramebuffer(gl.FRAMEBUFFER, fbos[nextIdx]);
      gl.viewport(0, 0, gridWidth, gridHeight);
      gl.useProgram(simProgram);

      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, textures[currentIdx]);
      gl.uniform1i(simStateLoc, 0);
      gl.uniform2f(simResLoc, gridWidth, gridHeight);

      gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer);
      gl.enableVertexAttribArray(simPosLoc);
      gl.vertexAttribPointer(simPosLoc, 2, gl.FLOAT, false, 0, 0);

      gl.drawArrays(gl.TRIANGLES, 0, 6);

      currentIdx = nextIdx;
    }

    function renderDisplay(transitionProgress) {
      // Render to screen
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.useProgram(displayProgram);

      gl.activeTexture(gl.TEXTURE0);
      gl.bindTexture(gl.TEXTURE_2D, textures[currentIdx]);
      gl.uniform1i(dispStateLoc, 0);

      gl.uniform2f(dispGridResLoc, gridWidth, gridHeight);
      gl.uniform1f(dispCellPixelLoc, cellPixelSize);
      gl.uniform1f(dispTransLoc, transitionProgress);
      gl.uniform3f(dispColorBgLoc, colorBg[0], colorBg[1], colorBg[2]);
      gl.uniform3f(dispColorCellLoc, colorCell[0], colorCell[1], colorCell[2]);

      gl.bindBuffer(gl.ARRAY_BUFFER, quadBuffer);
      gl.enableVertexAttribArray(dispPosLoc);
      gl.vertexAttribPointer(dispPosLoc, 2, gl.FLOAT, false, 0, 0);

      gl.drawArrays(gl.TRIANGLES, 0, 6);
    }

    // Initialize layout & sizing
    resize();

    let lastStepTime = performance.now();
    let lastEntropyTime = performance.now();
    let animationFrameId = null;

    const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');

    function loop(now) {
      if (prefersReducedMotion && prefersReducedMotion.matches) {
        // Display single static subtle pattern without ticking
        renderDisplay(1.0);
        return;
      }

      const elapsed = now - lastStepTime;

      if (elapsed >= STEP_INTERVAL) {
        stepSimulation();
        lastStepTime = now;
      }

      if (now - lastEntropyTime >= ENTROPY_INTERVAL) {
        injectEntropy();
        lastEntropyTime = now;
      }

      const transitionTime = Math.min(now - lastStepTime, TRANSITION_DURATION);
      const transitionProgress = transitionTime / TRANSITION_DURATION;

      renderDisplay(transitionProgress);

      animationFrameId = requestAnimationFrame(loop);
    }

    // Start loop
    animationFrameId = requestAnimationFrame(loop);

    // Event listeners
    let resizeTimer = null;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        resize();
        if (prefersReducedMotion && prefersReducedMotion.matches) {
          renderDisplay(1.0);
        }
      }, 150);
    });

    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        updateThemeColors();
        if (prefersReducedMotion && prefersReducedMotion.matches) {
          renderDisplay(1.0);
        }
      });

      prefersReducedMotion.addEventListener('change', () => {
        if (prefersReducedMotion.matches) {
          if (animationFrameId) cancelAnimationFrame(animationFrameId);
          renderDisplay(1.0);
        } else {
          lastStepTime = performance.now();
          lastEntropyTime = performance.now();
          animationFrameId = requestAnimationFrame(loop);
        }
      });
    }

    // Tab visibility handling to pause simulation and save battery
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        if (animationFrameId) {
          cancelAnimationFrame(animationFrameId);
          animationFrameId = null;
        }
      } else {
        lastStepTime = performance.now();
        lastEntropyTime = performance.now();
        if (!animationFrameId && !(prefersReducedMotion && prefersReducedMotion.matches)) {
          animationFrameId = requestAnimationFrame(loop);
        }
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGameOfLife);
  } else {
    initGameOfLife();
  }
})();
