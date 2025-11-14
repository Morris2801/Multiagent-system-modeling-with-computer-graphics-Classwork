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
        id: 'pivot',
        transforms: {
            t: {
                x: 600,
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
        id: 'smiley',
        transforms: {
            t: {
                x: 600, 
                y: 300,
            },
            rr: {
                z: 0, 
            },
            s: {
                x: 1,
                y: 1,
            }
        },
        colors: {
            face: [1, 1, 0, 1],
            leftEye: [0, 0, 0, 1],
            rightEye: [0, 0, 0, 1],
            mouth: [1, 0, 0, 1],
        }
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
    // Creación de cara
    // Creación de pivote cuadrado
    const square = generateData(4, objects.pivot.size);
    const squareBufferInfo = twgl.createBufferInfoFromArrays(gl, square);
    const squareVao = twgl.createVAOFromBufferInfo(gl, programInfo, squareBufferInfo);
    objects.pivot.vao = squareVao;
    objects.pivot.bufferInfo = squareBufferInfo;
    
    const arrays = caraFeliz(100, 25, 50);
    const bufferInfo = twgl.createBufferInfoFromArrays(gl, arrays);
    const vao = twgl.createVAOFromBufferInfo(gl, programInfo, bufferInfo);
    objects.smiley.vao = vao;
    objects.smiley.bufferInfo = bufferInfo;
    drawScene(gl, programInfo);
}

// Function to do the actual display of the objects
function drawScene(gl, programInfo) {
    gl.useProgram(programInfo.program);

    for (const object of Object.values(objects)) {
        let transforms = M3.identity();
        if (object.id === 'pivot') {
            const pivotPos = [object.transforms.t.x, object.transforms.t.y];
            const pivotScale = [object.transforms.s.x, object.transforms.s.y];
            transforms = M3.multiply(M3.scale(pivotScale), transforms);
            transforms = M3.multiply(M3.translation(pivotPos), transforms);
            let uniforms = {
                u_resolution: [gl.canvas.width, gl.canvas.height],
                u_transforms: transforms,
                u_color: object.color,
            };
            twgl.setUniforms(programInfo, uniforms);
            gl.bindVertexArray(object.vao);
            twgl.drawBufferInfo(gl, object.bufferInfo);
            
        } else if (object.id === 'smiley') {
            // Para la cara, aplicar transformaciones respecto al pivote
            const angle = object.transforms.rr.z * Math.PI / 180;
            const facePos = [object.transforms.t.x, object.transforms.t.y];
            const faceScale = [object.transforms.s.x, object.transforms.s.y];
            const pivotPos = [objects.pivot.transforms.t.x, objects.pivot.transforms.t.y];
            
            // Orden: Escala -> Trasladar cara -> Mover a origen (pivote) -> Rotar -> Regresar pivote
            transforms = M3.multiply(M3.scale(faceScale), transforms);
            transforms = M3.multiply(M3.translation(facePos), transforms);
            transforms = M3.multiply(M3.translation([-pivotPos[0], -pivotPos[1]]), transforms);
            transforms = M3.multiply(M3.rotation(angle), transforms);
            transforms = M3.multiply(M3.translation(pivotPos), transforms);
            
            gl.bindVertexArray(object.vao);
            
            // Dibujar cara (amarilla)
            let uniforms = {
                u_resolution: [gl.canvas.width, gl.canvas.height],
                u_transforms: transforms,
                u_color: object.colors.face,
            };
            twgl.setUniforms(programInfo, uniforms);
            gl.drawElements(gl.TRIANGLES, 300, gl.UNSIGNED_SHORT, 0);
            
            // Dibujar ojo izquierdo (negro)
            uniforms.u_color = object.colors.leftEye;
            twgl.setUniforms(programInfo, uniforms);
            gl.drawElements(gl.TRIANGLES, 60, gl.UNSIGNED_SHORT, 300 * 2);
            
            // Dibujar ojo derecho (negro)
            uniforms.u_color = object.colors.rightEye;
            twgl.setUniforms(programInfo, uniforms);
            gl.drawElements(gl.TRIANGLES, 60, gl.UNSIGNED_SHORT, (300 + 60) * 2);
            
            // Dibujar boca (roja)
            uniforms.u_color = object.colors.mouth;
            twgl.setUniforms(programInfo, uniforms);
            gl.drawElements(gl.TRIANGLES, 150, gl.UNSIGNED_SHORT, (300 + 60 + 60) * 2);
        }
    }

    requestAnimationFrame(() => drawScene(gl, programInfo));
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
