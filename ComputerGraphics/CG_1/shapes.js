/*
    A01029647 Mauricio Monroy González
    Tarea 1 - Carita feliz con pivote manipulable
    2D Graphics with WebGL

    Este archivo contiene las funciones para crear diferentes figuras en 2D y 3D,
    incluyendo una carita feliz en 2D.
 */

// Create the data for the vertices of a polygon with the shape of the
// letter F. This is useful to view the transformations on the object.
function shapeF() {
    let arrays = {
        a_position: {
            numComponents: 2,
            data: [
                // Letter F
                0, 0,
                0, 200,
                40, 200,
                40, 0,
                40, 40,
                200, 40,
                200, 0,
                40, 120,
                150, 120,
                150, 80,
                40, 80,
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                // Front face
                0, 1, 2,
                2, 3, 0,
                3, 4, 5,
                5, 6, 3, 
                7, 8, 9,
                9, 10, 7,
            ]
        }
    };

    return arrays;
}

function diamond(size) {
    let arrays = {
        a_position: {
            numComponents: 2,
            data: [
                // A diamond shape
                size, 0,
                0, size,
                -size, 0,
                0, -size,
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                // Front face
                0, 1, 2,
                2, 3, 0,
            ]
        }
    };

    return arrays;
}

function car2D() {
    let arrays = {
        a_position: {
            numComponents: 2,
            data: [
                -100,  -40,
                 -40,  -40,
                  40,  -40,
                 100,  -40,
                 100,  -20,
                  40,   10,
                 -40,   10,
                -100,   20,
                 -30,   40,
                  24,   30,
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                0, 1, 6,      0, 6, 7,    // Car back
                1, 2, 5,      1, 5, 6,    // Car middle
                2, 3, 4,      2, 4, 5,    // Car front
                6, 5, 9,      6, 9, 8     // Car top
            ]
        }
    }

    return arrays;
}


// Create the data for a cube where each face has a different color
function cubeFaceColors(size) {
    let arrays = {
        a_position: {
            numComponents: 3,
            data: [
                // Front Face
                -1.0, -1.0,  1.0,
                1.0, -1.0,  1.0,
                1.0,  1.0,  1.0,
                -1.0,  1.0,  1.0,

                // Back face
                -1.0, -1.0, -1.0,
                -1.0,  1.0, -1.0,
                1.0,  1.0, -1.0,
                1.0, -1.0, -1.0,

                // Top face
                -1.0,  1.0, -1.0,
                -1.0,  1.0,  1.0,
                1.0,  1.0,  1.0,
                1.0,  1.0, -1.0,

                // Bottom face
                -1.0, -1.0, -1.0,
                1.0, -1.0, -1.0,
                1.0, -1.0,  1.0,
                -1.0, -1.0,  1.0,

                // Right face
                1.0, -1.0, -1.0,
                1.0,  1.0, -1.0,
                1.0,  1.0,  1.0,
                1.0, -1.0,  1.0,

                // Left face
                -1.0, -1.0, -1.0,
                -1.0, -1.0,  1.0,
                -1.0,  1.0,  1.0,
                -1.0,  1.0, -1.0
            ].map(e => size * e)
        },
        a_normal: {
            numComponents: 3,
            data: [
                // Front Face
                0, 0, 1,
                0, 0, 1,
                0, 0, 1,
                0, 0, 1,

                // Back face
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,
                0, 0, -1,

                // Top face
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,
                0, 1, 0,

                // Bottom face
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,
                0, -1, 0,

                // Right face
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,
                1, 0, 0,

                // Left face
                -1, 0, 0,
                -1, 0, 0,
                -1, 0, 0,
                -1, 0, 0,
            ]
        },
        a_color: {
            numComponents: 4,
            data: [
                // Front face
                1, 0, 0, 1, // v_1
                1, 0, 0, 1, // v_1
                1, 0, 0, 1, // v_1
                1, 0, 0, 1, // v_1
                // Back Face
                0, 1, 0, 1, // v_2
                0, 1, 0, 1, // v_2
                0, 1, 0, 1, // v_2
                0, 1, 0, 1, // v_2
                // Top Face
                0, 0, 1, 1, // v_3
                0, 0, 1, 1, // v_3
                0, 0, 1, 1, // v_3
                0, 0, 1, 1, // v_3
                // Bottom Face
                1, 1, 0, 1, // v_4
                1, 1, 0, 1, // v_4
                1, 1, 0, 1, // v_4
                1, 1, 0, 1, // v_4
                // Right Face
                0, 1, 1, 1, // v_5
                0, 1, 1, 1, // v_5
                0, 1, 1, 1, // v_5
                0, 1, 1, 1, // v_5
                // Left Face
                1, 0, 1, 1, // v_6
                1, 0, 1, 1, // v_6
                1, 0, 1, 1, // v_6
                1, 0, 1, 1, // v_6
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                0, 1, 2,      0, 2, 3,    // Front face
                4, 5, 6,      4, 6, 7,    // Back face
                8, 9, 10,     8, 10, 11,  // Top face
                12, 13, 14,   12, 14, 15, // Bottom face
                16, 17, 18,   16, 18, 19, // Right face
                20, 21, 22,   20, 22, 23  // Left face
            ]
        }
    };

    return arrays;
}

// Create the data for a cube with each vertex in a different color
function cubeVertexColors(size) {
    let arrays = {
        a_position: {
            numComponents: 3,
            data: [
                1,  1,  1, // v_0
                1, -1,  1, // v_1
                -1, -1,  1, // v_2
                -1,  1,  1, // v_3
                1,  1, -1, // v_4
                1, -1, -1, // v_5
                -1, -1, -1, // v_6
                -1,  1, -1, // v_7
            ].map(e => size * e)
        },
        a_color: {
            numComponents: 4,
            data: [
                1, 1, 1, 1, // v_0
                1, 0, 0, 1, // v_1
                0, 1, 0, 1, // v_2
                0, 0, 1, 1, // v_3
                0, 0, 0, 1, // v_4
                1, 1, 0, 1, // v_5
                0, 1, 1, 1, // v_6
                1, 0, 1, 1, // v_7
            ]
        },
        indices: {
            numComponents: 3,
            data: [
                // Front face
                0, 2, 1,
                2, 0, 3,
                // Top face
                0, 5, 4,
                5, 0, 1,
                // Left face
                1, 6, 5,
                6, 1, 2,
                // Right face
                0, 7, 3,
                7, 0, 4,
                // Bottom face
                2, 7, 6,
                7, 2, 3,
                // Back face
                4, 6, 7,
                6, 4, 5,
            ]
        }
    };

    return arrays;
}


function generateData(sides, radius) {
    // The arrays are initially empty
    let arrays =
    {
        // Two components for each position in 2D
        a_position: { numComponents: 2, data: [] },
        // Four components for a color (RGBA)
        a_color:    { numComponents: 4, data: [] },
        // Three components for each triangle, the 3 vertices
        indices:  { numComponents: 3, data: [] }
    };

    // Initialize the center vertex, at the origin and with white color
    arrays.a_position.data.push(0);
    arrays.a_position.data.push(0);
    arrays.a_color.data.push(1);
    arrays.a_color.data.push(1);
    arrays.a_color.data.push(1);
    arrays.a_color.data.push(1);

    let angleStep = 2 * Math.PI / sides;
    // Loop over the sides to create the rest of the vertices
    for (let s=0; s<sides; s++) {
        let angle = angleStep * s;
        // Generate the coordinates of the vertex
        let x = radius * Math.cos(angle);
        let y = radius * Math.sin(angle);
        arrays.a_position.data.push(x);
        arrays.a_position.data.push(y);
        // Generate a random color for the vertex
        arrays.a_color.data.push(Math.random());
        arrays.a_color.data.push(Math.random());
        arrays.a_color.data.push(Math.random());
        arrays.a_color.data.push(1);
        // Define the triangles, in counter clockwise order
        arrays.indices.data.push(0); 
        arrays.indices.data.push(s + 1);
        arrays.indices.data.push(((s + 2) <= sides) ? (s + 2) : 1);
    }
    // console.log(arrays);
    return arrays;
}

function generateSemiCircle(sides, radius, yOffset) {
    let arrays = {
        a_position: { numComponents: 2, data: [] },
        a_color:    { numComponents: 4, data: [] },
        indices:    { numComponents: 3, data: [] }
    };
    arrays.a_position.data.push(0, yOffset);
    arrays.a_color.data.push(1, 0, 0, 1); 
    
    let angleStep = Math.PI / sides;
    for (let s = 0; s <= sides; s++) {
        let angle = Math.PI + angleStep * s; 
        let x = radius * Math.cos(angle);
        let y = yOffset + radius * Math.sin(angle);
        arrays.a_position.data.push(x, y);
        arrays.a_color.data.push(1, 0, 0, 1);        
        if (s > 0) {
            arrays.indices.data.push(0, s, s + 1);
        }
    }
    
    return arrays;
}


function caraFeliz(faceRadius, eyeRad, smileLen){
    let arrays ={
        a_position: { numComponents: 2, data: [] },
        a_color:    { numComponents: 4, data: [] },
        indices:  { numComponents: 3, data: [] }
    };
    let indexOffset = 0;
    //cara: circuloGrande    
    let big = generateData(100,faceRadius);
    for (let i = 0; i < big.a_color.data.length; i+=4){
        big.a_color.data[i] = 1;
        big.a_color.data[i+1] = 1;
        big.a_color.data[i+2] = 0;
        big.a_color.data[i+3] = 1;
    }
    arrays.a_position.data.push(...big.a_position.data);
    arrays.a_color.data.push(...big.a_color.data);
    arrays.indices.data.push(...big.indices.data);
    indexOffset += (big.a_position.data.length / 2);
    //ojoIzq
    let leftEye = generateData(20, eyeRad);
    for (let i = 0; i < leftEye.a_position.data.length; i+=2){
        leftEye.a_position.data[i] += -faceRadius * 0.3;
        leftEye.a_position.data[i+1] += faceRadius * 0.3;  
    }
    for (let i = 0; i < leftEye.a_color.data.length; i += 4) {
        leftEye.a_color.data[i] = 0;
        leftEye.a_color.data[i+1] = 0;
        leftEye.a_color.data[i+2] = 0;
        leftEye.a_color.data[i+3] = 1;
    }
    for (let i = 0; i < leftEye.indices.data.length; i++) {
        leftEye.indices.data[i] += indexOffset;
    } 
    arrays.a_position.data.push(...leftEye.a_position.data);
    arrays.a_color.data.push(...leftEye.a_color.data);
    arrays.indices.data.push(...leftEye.indices.data);
    indexOffset += (leftEye.a_position.data.length / 2);
    //ojoDer
    let rightEye = generateData(20, eyeRad);
    for (let i = 0; i < rightEye.a_position.data.length; i += 2) {
        rightEye.a_position.data[i] += faceRadius * 0.3;
        rightEye.a_position.data[i+1] += faceRadius * 0.3;
    }
    for (let i = 0; i < rightEye.a_color.data.length; i += 4) {
        rightEye.a_color.data[i] = 0;
        rightEye.a_color.data[i+1] = 0;
        rightEye.a_color.data[i+2] = 0;
        rightEye.a_color.data[i+3] = 1;
    }
    for (let i = 0; i < rightEye.indices.data.length; i++) {
        rightEye.indices.data[i] += indexOffset;
    }
    arrays.a_position.data.push(...rightEye.a_position.data);
    arrays.a_color.data.push(...rightEye.a_color.data);
    arrays.indices.data.push(...rightEye.indices.data);
    indexOffset += (rightEye.a_position.data.length / 2);
    //boca 
    let mouth = generateSemiCircle(smileLen, faceRadius * 0.5, -0.4 * faceRadius);
    for (let i = 0; i < mouth.indices.data.length; i++) {
        mouth.indices.data[i] += indexOffset;
    }
    arrays.a_position.data.push(...mouth.a_position.data);
    arrays.a_color.data.push(...mouth.a_color.data);
    arrays.indices.data.push(...mouth.indices.data);
    
    return arrays;
}



export { shapeF, diamond, cubeFaceColors, cubeVertexColors, car2D, generateData, caraFeliz };