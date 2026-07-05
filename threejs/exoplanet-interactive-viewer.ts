import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

type FocusFrame = {
  center: THREE.Vector3;
  radius: number;
};

const STAR_COLOR = new THREE.Color(0xffffff);
const CAMERA_DIRECTION = new THREE.Vector3(1, 0.28, 0.42).normalize();

/** Minimum screen-space diameter in pixels any star should occupy. */
const MIN_STAR_PX = 0.5;

function getCanvas(id: string): HTMLCanvasElement {
  const el = document.getElementById(id);
  if (!el) throw new Error(`Missing element #${id}`);
  if (!(el instanceof HTMLCanvasElement)) throw new Error(`#${id} is not a <canvas>`);
  return el;
}

function percentile(values: number[], value: number): number {
  if (values.length === 0) return 0;
  const index = Math.min(values.length - 1, Math.max(0, Math.floor((values.length - 1) * value)));
  return values[index];
}

function computeFocusFrame(model: THREE.Object3D): FocusFrame {
  const box = new THREE.Box3().setFromObject(model);
  const fallbackCenter = box.getCenter(new THREE.Vector3());
  const fallbackRadius = Math.max(box.getSize(new THREE.Vector3()).length() * 0.5, 1);
  const worldPositions: THREE.Vector3[] = [];

  model.updateWorldMatrix(true, true);
  model.traverse((obj) => {
    if (!(obj as THREE.Mesh).isMesh) return;
    const mesh = obj as THREE.Mesh;
    const position = new THREE.Vector3();
    mesh.getWorldPosition(position);
    worldPositions.push(position);
  });

  if (worldPositions.length === 0) {
    return { center: fallbackCenter, radius: fallbackRadius };
  }

  const center = worldPositions.reduce((sum, point) => sum.add(point), new THREE.Vector3()).multiplyScalar(1 / worldPositions.length);
  const radii = worldPositions.map((point) => point.distanceTo(center)).sort((a, b) => a - b);
  const radius = Math.max(percentile(radii, 0.9), fallbackRadius * 0.02, 1);

  return { center, radius };
}

function promoteStarMaterial(_material: THREE.Material): THREE.Material {
  return new THREE.MeshBasicMaterial({
    color: STAR_COLOR,
    toneMapped: false,
    side: THREE.DoubleSide,
  });
}

/**
 * Compute how many world-units span one pixel at a given distance from the camera.
 * For a perspective camera, the visible height at distance `d` is `2 * d * tan(fovV/2)`.
 * Dividing that by the viewport height in pixels gives world-units-per-pixel.
 */
function pixelSizeAtDistance(camera: THREE.PerspectiveCamera, distance: number): number {
  const fovRad = (camera.fov * Math.PI) / 180;
  const visibleHeight = 2 * distance * Math.tan(fovRad / 2);
  return visibleHeight / window.innerHeight;
}

function setupHoverTooltip(
  canvasEl: HTMLCanvasElement,
  scene: THREE.Scene,
  camera: THREE.PerspectiveCamera,
  allMeshes: THREE.Mesh[],
) {
  const tooltip = document.getElementById('mesh-tooltip');
  const label = document.getElementById('mesh-tooltip-label');
  if (!tooltip || !label) return;

  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();

  function hideTooltip() {
    tooltip!.classList.remove('visible');
  }

  canvasEl.addEventListener('mousemove', (event: MouseEvent) => {
    const rect = canvasEl.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(allMeshes, false);

    if (intersects.length === 0) {
      hideTooltip();
      return;
    }

    const hit = intersects[0];
    const mesh = hit.object as THREE.Mesh;

    // Project world hit point to screen
    const worldPoint = hit.point.clone();
    const projected = worldPoint.clone().project(camera);

    // Behind camera check
    if (projected.z > 1) {
      hideTooltip();
      return;
    }

    // NDC to screen pixels
    const screenX = (projected.x * 0.5 + 0.5) * window.innerWidth;
    const screenY = (-projected.y * 0.5 + 0.5) * window.innerHeight;

    // Set label text
    label.textContent = mesh.name || 'unnamed';

    // Anchor tooltip container's top-left at the mesh screen point.
    tooltip.style.left = `${screenX}px`;
    tooltip.style.top = `${screenY}px`;
    tooltip.classList.add('visible');

    // Draw line from mesh anchor (0,0 in container space) to label's bottom-left corner.
    const labelRect = label.getBoundingClientRect();
    const containerRect = tooltip.getBoundingClientRect();
    const targetX = labelRect.left - containerRect.left;
    const targetY = labelRect.top + labelRect.height - containerRect.top;

    const lineDiv = tooltip.querySelector('#mesh-tooltip-line') as HTMLElement;
    const distance = Math.hypot(targetX, targetY);
    const angle = Math.atan2(targetY, targetX) * (180 / Math.PI);

    lineDiv.style.width = `${distance}px`;
    lineDiv.style.transform = `rotate(${angle}deg)`;
  });

  window.addEventListener('resize', () => {
    hideTooltip();
  });
}

function main() {
  const canvasEl = getCanvas('canvas');

  // Disable global CRT scanlines for this fullscreen app.
  document.body.classList.add('no-scanlines');

  const gl2 = canvasEl.getContext('webgl2', { antialias: true, alpha: false });
  const gl1 = gl2 ? null : canvasEl.getContext('webgl', { antialias: true, alpha: false });
  if (!gl2 && !gl1) throw new Error('No WebGL context available');

  const renderer = new THREE.WebGLRenderer({
    canvas: canvasEl,
    context: (gl2 || gl1) as WebGLRenderingContext,
    antialias: true,
    alpha: false,
    logarithmicDepthBuffer: true,
    powerPreference: 'high-performance',
    preserveDrawingBuffer: false,
  });

  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor(0x000000, 1);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);

  const camera = new THREE.PerspectiveCamera(45, 1, 0.001, 1e12);
  camera.position.set(10000, 500, 0);
  camera.lookAt(0, 0, 0);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.target.set(0, 0, 0);
  controls.update();

  const loader = new GLTFLoader();

  /** Mesh paired with its original scale for distance-based dynamic resizing. */
  interface StarEntry {
    mesh: THREE.Mesh;
    originalScale: number;
  }
  const allMeshes: THREE.Mesh[] = [];
  const starEntries: StarEntry[] = [];

  loader.load(
    './static/starmap.glb',
    (gltf: import('three/examples/jsm/loaders/GLTFLoader.js').GLTF) => {
      const model = gltf.scene;
      const materialCache = new Map<THREE.Material, THREE.Material>();

      model.traverse((obj) => {
        if (!(obj as THREE.Mesh).isMesh) return;
        const mesh = obj as THREE.Mesh;
        allMeshes.push(mesh);

        // Store the original uniform scale (average of x/y/z)
        const origScale = (mesh.scale.x + mesh.scale.y + mesh.scale.z) / 6;
        starEntries.push({ mesh, originalScale: origScale || 1 });

        const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
        const upgraded = materials.map((material) => {
          if (!materialCache.has(material)) {
            materialCache.set(material, promoteStarMaterial(material));
          }
          return materialCache.get(material)!;
        });

        mesh.material = Array.isArray(mesh.material) ? upgraded : upgraded[0];
        mesh.frustumCulled = false;
      });

      scene.add(model);

      // Setup hover tooltip after all meshes are collected
      setupHoverTooltip(canvasEl, scene, camera, allMeshes, starEntries);

      // fitCameraToFrame(camera, controls, computeFocusFrame(model));
    },
    undefined,
    (err: unknown) => {
      console.error(err);
    }
  );

  function resize() {
    const w = Math.max(1, Math.floor(window.innerWidth));
    const h = Math.max(1, Math.floor(window.innerHeight));
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h, false);
  }

  window.addEventListener('resize', resize);
  resize();

  /** Temporary vector reused in animate() to avoid per-frame allocations. */
  const _tempCamPos = new THREE.Vector3();
  const _tempMeshPos = new THREE.Vector3();

  function animate() {
    requestAnimationFrame(animate);
    controls.update();

    // Distance-based dynamic scaling: keep every star visible regardless of zoom.
    camera.getWorldPosition(_tempCamPos);
    for (const entry of starEntries) {
      entry.mesh.getWorldPosition(_tempMeshPos);
      const distance = _tempCamPos.distanceTo(_tempMeshPos);
      const pxSize = pixelSizeAtDistance(camera, distance);
      const minWorldSize = MIN_STAR_PX * pxSize;
      const targetScale = Math.max(entry.originalScale, minWorldSize);
      entry.mesh.scale.setScalar(targetScale);
    }

    renderer.render(scene, camera);
  }
  animate();
}

if (typeof window !== 'undefined') {
  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', main, { once: true });
  } else {
    main();
  }
}