/*
    A01029647 Mauricio Monroy González
    Tarea 1 - Carita feliz con pivote manipulable
    2D Graphics with WebGL

    Este archivo contiene la implementación de una carita feliz en un entorno WebGL2,
    donde se puede manipular la posición, escala y rotación de la carita
    alrededor de un pivote cuadrado que también es manipulable en posición, escala y color.
 */

'use strict';

import * as twgl from 'twgl-base.js';
import { generateData, caraFeliz } from './shapes.js';
import { M3 } from './2d-lib.js';
import GUI from 'lil-gui';

// Define the shader code, using GLSL 3.00

const vsGLSL = `#version 300 es
in vec2 a_position;

uniform vec2 u_resolution;
uniform mat3 u_transforms;

void main() {
    vec2 position = (u_transforms * vec3(a_position, 1)).xy;
    vec2 zeroToOne = position / u_resolution;
    vec2 zeroToTwo = zeroToOne * 2.0;
    vec2 clipSpace = zeroToTwo - 1.0;
    gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
}
`;

const fsGLSL = `#version 300 es
precision highp float;

uniform vec4 u_color;

out vec4 outColor;

void main() {
    outColor = u_color;
}
`;

// Estructuras con condiciones iniciales
const objects = {
    pivot: {
        transforms: {
            t: {
                x: 600 ,
                y: 300,
            },
            s: {
                x: 1,
                y: 1,
            }
        },
        color: [0, 0, 0, 1],
        size: 10,
    },
    smiley: {
        transforms: {
            t: {
                x: 600, 
                y: 300,
            },
            rr: {
                z: 180,
            },
            s: {
                x: 1,
                y: 1,
            }
        },
    }
}

// Initialize the WebGL environmnet
function main() {
    const canvas = document.querySelector('canvas');
    const gl = canvas.getContext('webgl2');
    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    setupUI(gl);

    const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);
    // creación de cara
    const arrays = caraFeliz(100, 25, 50);
    const bufferInfo = twgl.createBufferInfoFromArrays(gl, arrays);
    const vao = twgl.createVAOFromBufferInfo(gl, programInfo, bufferInfo);
    // creación de pivote cuadrado
    const square = generateData(4, objects.pivot.size);
    const squareBufferInfo = twgl.createBufferInfoFromArrays(gl, square);
    const squareVao = twgl.createVAOFromBufferInfo(gl, programInfo, squareBufferInfo);

    drawScene(gl, vao, programInfo, bufferInfo, squareVao, squareBufferInfo);
}

// Function to do the actual display of the objects
function drawScene(gl, vao, programInfo, bufferInfo, squareVao, squareBufferInfo) {
    gl.useProgram(programInfo.program);

    // cara --------------------
    const angle = objects.smiley.transforms.rr.z * Math.PI / 180;
    const faceT = [
        objects.smiley.transforms.t.x,
        objects.smiley.transforms.t.y
    ];
    const scale = [
        objects.smiley.transforms.s.x,
        objects.smiley.transforms.s.y
    ];
    const pivotT = [
        objects.pivot.transforms.t.x,
        objects.pivot.transforms.t.y
    ];
    // Matrices 
    const traFaceMat = M3.translation(faceT);
    const scaMat = M3.scale(scale);
    const traToPivot = M3.translation([-pivotT[0], -pivotT[1]]); //mover pivote a origen
    const rotMat = M3.rotation(angle); //rotar
    const traFromPivot = M3.translation([pivotT[0], pivotT[1]]); // regresar posición del pivote

    //transformaciones
    // 1 Escalar 2 mover 3) Mover pivote -> rotar ->regresar pivote
    let transformsSmiley = M3.identity();
    transformsSmiley = M3.multiply(scaMat, transformsSmiley);
    transformsSmiley = M3.multiply(traFaceMat, transformsSmiley);
    transformsSmiley = M3.multiply(traToPivot, transformsSmiley);
    transformsSmiley = M3.multiply(rotMat, transformsSmiley);
    transformsSmiley = M3.multiply(traFromPivot, transformsSmiley);
    gl.bindVertexArray(vao);
    let uniforms = {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: transformsSmiley,
        u_color: [1, 1, 0, 1], // cara amarilla
    };
    twgl.setUniforms(programInfo, uniforms);
    gl.drawElements(gl.TRIANGLES, 300, gl.UNSIGNED_SHORT, 0);
    uniforms.u_color = [0, 0, 0, 1]; // ojo izq
    twgl.setUniforms(programInfo, uniforms);
    gl.drawElements(gl.TRIANGLES, 60, gl.UNSIGNED_SHORT, 300 * 2);
    uniforms.u_color = [0, 0, 0, 1]; // ojo der
    twgl.setUniforms(programInfo, uniforms);
    gl.drawElements(gl.TRIANGLES, 60, gl.UNSIGNED_SHORT, (300 + 60) * 2);
    uniforms.u_color = [1, 0, 0, 1]; // boca
    twgl.setUniforms(programInfo, uniforms);
    gl.drawElements(gl.TRIANGLES, 150, gl.UNSIGNED_SHORT, (300 + 60 + 60) * 2);

    // pivote ------------------
    const pivotScale = [
        objects.pivot.transforms.s.x,
        objects.pivot.transforms.s.y
    ];
    const pivotScaMat = M3.scale(pivotScale);
    const pivotTraMat = M3.translation(pivotT);
    let transformsPivot = M3.identity();
    transformsPivot = M3.multiply(pivotScaMat, transformsPivot);
    transformsPivot = M3.multiply(pivotTraMat, transformsPivot);
    let uniformsSquare = {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: transformsPivot,
        u_color: objects.pivot.color,
    };
    gl.bindVertexArray(squareVao);
    twgl.setUniforms(programInfo, uniformsSquare);
    twgl.drawBufferInfo(gl, squareBufferInfo);
    requestAnimationFrame(() =>
        drawScene(gl, vao, programInfo, bufferInfo, squareVao, squareBufferInfo)
    );
}

function setupUI(gl) {
    const gui = new GUI();
    // Controles de pivote-------------------------
    const pivotFolder = gui.addFolder('Pivot');
    pivotFolder.add(objects.pivot.transforms.t, 'x', 0, gl.canvas.width).name('Position X');
    pivotFolder.add(objects.pivot.transforms.t, 'y', 0, gl.canvas.height).name('Position Y');
    const pivotScaFolder = pivotFolder.addFolder('Scale');
    pivotScaFolder.add(objects.pivot.transforms.s, 'x', -5, 5).name('Scale X');
    pivotScaFolder.add(objects.pivot.transforms.s, 'y', -5, 5).name('Scale Y');
    pivotFolder.addColor(objects.pivot, 'color').name('Pivot Color');
    pivotFolder.open();

    // Controles de carita ------------------------
    const smileyFolder = gui.addFolder('Smiley Face');
    const smileyTraFolder = smileyFolder.addFolder('Position');
    smileyTraFolder.add(objects.smiley.transforms.t, 'x', 0, gl.canvas.width).name('Position X');
    smileyTraFolder.add(objects.smiley.transforms.t, 'y', 0, gl.canvas.height).name('Position Y');
    const smileyRotFolder = smileyFolder.addFolder('Rotation');
    smileyRotFolder.add(objects.smiley.transforms.rr, 'z', 0, 360).name('Angle (degrees)');
    const smileyScaFolder = smileyFolder.addFolder('Scale');
    smileyScaFolder.add(objects.smiley.transforms.s, 'x', -5, 5).name('Scale X');
    smileyScaFolder.add(objects.smiley.transforms.s, 'y', -5, 5).name('Scale Y');
    smileyFolder.open();
}

main()
