import * as THREE from 'three';
import { MTLLoader } from 'https://cdn.jsdelivr.net/npm/three@0.150.1/examples/jsm/loaders/MTLLoader.js';
import { OBJLoader } from 'https://cdn.jsdelivr.net/npm/three@0.150.1/examples/jsm/loaders/OBJLoader.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.150.1/examples/jsm/controls/OrbitControls.js';
import { RoomEnvironment } from 'RoomEnvironment';

const canvas = document.getElementById('three-canvas');
const emoji = document.getElementById('emoji');
const codeDisplay = document.getElementById('code');

let renderer, scene, camera, controls;
let pivots = [];
let animationFrameId = null;

function getEmojiCodeSequence(emojiChar) {
    return [...emojiChar].map(c => 'U+' + c.codePointAt(0).toString(16).toUpperCase());
}

function initThree() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 0, 5);

    renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setClearColor(0x000000, 0);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    const pmremGenerator = new THREE.PMREMGenerator(renderer);
    pmremGenerator.compileEquirectangularShader();
    const envMap = pmremGenerator.fromScene(new RoomEnvironment(), 0.2).texture;
    scene.environment = envMap;

    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;

    const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 1.5);
    scene.add(hemi);

    const rimLight = new THREE.DirectionalLight(0xffffff, 1);
    rimLight.position.set(10, 10, 5);
    rimLight.castShadow = true;
    rimLight.shadow.mapSize.width = 1024;
    rimLight.shadow.mapSize.height = 1024;
    rimLight.shadow.camera.near = 0.5;
    rimLight.shadow.camera.far = 50;
    scene.add(rimLight);

    const fillLight = new THREE.PointLight(0xffffff, 0.8);
    fillLight.position.set(-5, 5, 5);
    scene.add(fillLight);

    const ground = new THREE.Mesh(
        new THREE.PlaneGeometry(20, 20),
        new THREE.ShadowMaterial({ opacity: 0.3 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -1;
    ground.receiveShadow = true;
    scene.add(ground);
}

function clearScene() {
    pivots.forEach(p => scene.remove(p));
    pivots = [];
}

function loadEmojiSequence(codes) {
    clearScene();

    filtered.forEach((code, index) => {
        const mtlPath = `emoji_export/${code}/${code}.mtl`;
        const objPath = `emoji_export/${code}/${code}.obj`;

        const mtlLoader = new MTLLoader();
        mtlLoader.load(mtlPath, (materials) => {
            materials.preload();

            for (const key in materials.materials) {
                const mat = materials.materials[key];
                if (mat instanceof THREE.MeshPhongMaterial) {
                    mat.specular = new THREE.Color(1, 1, 1);
                    mat.shininess = 8;
                    mat.reflectivity = 0.1;
                    mat.envMap = scene.environment;
                }
            }

            const objLoader = new OBJLoader();
            objLoader.setMaterials(materials);
            objLoader.load(objPath, (object) => {
                object.traverse((child) => {
                    if (child.isMesh) {
                        child.castShadow = true;
                        child.receiveShadow = true;
                    }
                });

                const box = new THREE.Box3().setFromObject(object);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3()).length();

                object.position.sub(center);

                const pivot = new THREE.Object3D();
                pivot.add(object);
                pivot.position.x = index * (size + 0.5);
                scene.add(pivot);
                pivots.push(pivot);

                const totalWidth = (cofiltered.length - 1) * (size + 0.5);
                camera.position.set(0, 0, totalWidth + 1);
                camera.lookAt(0, 0, 0);
                controls.target.set(0, 0, 0);
                controls.update();
            });
        });
    });
}

function animate() {
    cancelAnimationFrame(animationFrameId);

    function loop() {
        animationFrameId = requestAnimationFrame(loop);
        pivots.forEach(pivot => {
            pivot.rotation.y += 0.005;
        });
        controls.update();
        renderer.render(scene, camera);
    }
    loop();
}

emoji.addEventListener('mouseenter', () => {
    canvas.style.display = 'block';

    const emojiChar = emoji.textContent.trim();
    const codeSequence = getEmojiCodeSequence(emojiChar);
    const visibleCodes = codeSequence.filter(code => code !== 'U+200D');

    codeDisplay.textContent = visibleCodes.join('_');

    if (!scene) {
        initThree();
    }

    loadEmojiSequence(visibleCodes);
    animate();
});

emoji.addEventListener('mouseleave', () => {
    canvas.style.display = 'none';
    cancelAnimationFrame(animationFrameId);
});

window.addEventListener('resize', () => {
    if (camera && renderer) {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }
});