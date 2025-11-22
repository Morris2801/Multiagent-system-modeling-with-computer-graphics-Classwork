/*
Tarea CG 2
Autor: Mauricio Monroy - A01029647
Descripción: programa que al compilarse con $node program.js {sides height radioBase radioPunta} genera un archivo .obj que represente a dicho cuerpo
    Utiliza triángulos, vértices y caras junto a sus respectivos vectores normales
*/


import fs from 'fs';

function writeFile(filename, content){
    fs.writeFileSync(filename, content);
}

// Lectura de inputs
function readArgs(){
    const args = process.argv.slice(2); // Ignora "node program.js" de la terminal
    
    let sides = parseInt(args[0]);
    let height = parseFloat(args[1]);
    let baseRadius = parseFloat(args[2]);
    let topRadius = parseFloat(args[3]);
    
    // Valores default si en entrada están vacíos
    if (isNaN(sides) || sides < 3 || sides > 36){
        sides = 8;
    }
    if (isNaN(height) || height <= 0){
        height = 6.0;
    }
    if (isNaN(baseRadius) || baseRadius <= 0){
        baseRadius = 1.0;
    }
    if (isNaN(topRadius) || topRadius <= 0){
        topRadius = 0.8;
    }
    return [sides, height, baseRadius, topRadius];
}

// Cálculo de vértices
function vertices(params){
    let vertices = []
    let numSides = params[0];
    let height = params[1];
    let baseRadius = params[2];
    let topRadius = params[3];
    
    vertices.push({x:0.0, y:0.0, z:0.0});
    vertices.push({x:0.0, y:height, z:0.0}); 
    
    for (let i=0; i<numSides; i++){
        let angle = 2 * Math.PI * i / numSides;
        let xBase = baseRadius * Math.cos(angle);
        let zBase = baseRadius * Math.sin(angle);
        let xTop = topRadius * Math.cos(angle);
        let zTop = topRadius * Math.sin(angle);
        vertices.push({x:xBase, y:0.0, z:zBase}); // Centro en base
        vertices.push({x:xTop, y:height, z:zTop}); // Centro alto
    }
    return vertices;
}

// Cálculo de vectores normales
function normales(params, vertices){
    let normales = []
    let numSides = params[0];
    
    for (let i = 0; i < numSides; i++) {
        let nextIndex = (i + 1) % numSides;
        normales.push({x:0.0, y:-1.0, z:0.0});
        normales.push({x:0.0, y:1.0, z:0.0}); 
        let baseActualInd = 2 + (i * 2);
        let topActualInd = baseActualInd + 1;
        let baseNextInd = 2 + (nextIndex * 2);
        let v1 = vertices[baseActualInd];
        let v2 = vertices[topActualInd];
        let v3 = vertices[baseNextInd];
        // Creación de arista 1
        let borde1 = {
            x: v2.x - v1.x,
            y: v2.y - v1.y,
            z: v2.z - v1.z
        }
        // Creacióin de arista 2
        let borde2 = {
            x: v3.x - v1.x,
            y: v3.y - v1.y,
            z: v3.z - v1.z
        }
        // Creación de vector normal
        let normal = {
            x: borde1.y * borde2.z - borde1.z * borde2.y,
            y: borde1.z * borde2.x - borde1.x * borde2.z,
            z: borde1.x * borde2.y - borde1.y * borde2.x
        }
        
        // Normalización
        let length = Math.sqrt(normal.x * normal.x + normal.y * normal.y + normal.z * normal.z);
        normal.x /= length;
        normal.y /= length;
        normal.z /= length;
        
        normales.push(normal);
        normales.push(normal); // doble para cada cara lateral
    }
    return normales;
}

// Unión de aristas para formar caras
function genCaras(params){
    let caras = [];
    let numSides = params[0];
    
    for (let i=0; i<numSides; i++){
        let nextIndex = (i + 1) % numSides;
        let baseActualInd = 2 + (i * 2);
        let topActualInd = baseActualInd + 1;
        let baseNextInd = 2 + (nextIndex * 2);
        let topNextInd = baseNextInd + 1;
        let normBase = (i * 4) + 0;
        let normTop = (i * 4) + 1;
        let normSide1 = (i * 4) + 2;
        let normSide2 = (i * 4) + 3;
        let cara1 = {
            v1: baseNextInd,
            n1: normBase,
            v2: 0,
            n2: normBase,
            v3: baseActualInd,
            n3: normBase
        };
        caras.push(cara1);
        
        let cara2 = {
            v1: topActualInd,
            n1: normTop,
            v2: 1,
            n2: normTop,
            v3: topNextInd,
            n3: normTop
        };
        caras.push(cara2);
        let cara3 = {
            v1: baseActualInd,
            n1: normSide1,
            v2: baseNextInd,
            n2: normSide1,
            v3: topActualInd,
            n3: normSide1
        };
        caras.push(cara3);
        
        let cara4 = {
            v1: topNextInd,
            n1: normSide2,
            v2: topActualInd,
            n2: normSide2,
            v3: baseNextInd,
            n3: normSide2
        };
        caras.push(cara4);
    }
    return caras;
}

function formatFloat(num, decimals){
    return num.toFixed(decimals);
}

// Construcción de string para archivo .obj
function objString(params, vertices, normales, caras){
    let objStr = "";
    objStr += "# OBJ file building_" + params[0] + "_" + params[1] + "_" + params[2] + "_" + params[3] + ".obj\n";
    objStr += "# " + vertices.length + " vertices\n";
    for (let vertice of vertices) {
        objStr += "v " + formatFloat(vertice.x, 4) + " " + formatFloat(vertice.y, 4) + " " + formatFloat(vertice.z, 4) + "\n";
    }
    objStr += "# " + normales.length + " normals\n";
    for (let normal of normales) {
        objStr += "vn " + formatFloat(normal.x, 4) + " " + formatFloat(normal.y, 4) + " " + formatFloat(normal.z, 4) + "\n";
    }
    objStr += "# " + caras.length + " faces\n";
    for (let cara of caras) { 
        objStr += "f " + (cara.v1 + 1) + "//" + (cara.n1 + 1) + " " + (cara.v2 + 1) + "//" + (cara.n2 + 1) + " " + (cara.v3 + 1) + "//" + (cara.n3 + 1) + "\n";
    }
    return objStr;
}

// Llamadas a funciones
function main(){
    let params = readArgs();
    let verts = vertices(params);
    let norms = normales(params, verts);
    let faces = genCaras(params);
    let objstr = objString(params, verts, norms, faces);
    
    let filename = "building_" + params[0] + "_" + params[1] + "_" + params[2] + "_" + params[3] + ".obj";
    
    writeFile(filename, objstr);
    console.log(`File: ${filename}`);
}

main();