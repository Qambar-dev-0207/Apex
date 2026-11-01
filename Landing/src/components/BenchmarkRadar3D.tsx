"use client";

import React, { useEffect, useRef } from "react";
import * as THREE from "three";
import { useReducedMotion } from "motion/react";

interface BenchmarkRadar3DProps {
  selectedPillarIndex: number; // 0: Speed, 1: Quality, 2: Integrity, 3: Retrieval
}

const PILLAR_VERTICES: [number, number, number][] = [
  [0, 1.85, 0.2],       // Speed (Top)
  [1.75, -0.4, 0.8],    // Quality (Right front)
  [-1.75, -0.4, 0.8],   // Integrity (Left front)
  [0, -0.85, -1.75],    // Retrieval (Back base)
];

const PILLAR_COLORS = [
  0xff4a16, // Speed (Orange)
  0xe9d0ad, // Quality (Pearl)
  0x10b981, // Integrity (Emerald)
  0x38bdf8, // Retrieval (Sky)
];

export default function BenchmarkRadar3D({ selectedPillarIndex }: BenchmarkRadar3DProps) {
  const mountRef = useRef<HTMLDivElement>(null);
  const shouldReduceMotion = useReducedMotion();

  const selectedIndexRef = useRef(selectedPillarIndex);
  useEffect(() => {
    selectedIndexRef.current = selectedPillarIndex;
  }, [selectedPillarIndex]);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 320;
    const height = container.clientHeight || 260;

    // SCENE & CAMERA
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 50);
    camera.position.set(0, 0.4, 6.2);

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: "high-performance",
      });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.75));
      renderer.setClearColor(0x000000, 0);
      container.appendChild(renderer.domElement);
    } catch {
      return;
    }

    // LIGHTS
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0xff4a16, 2.5, 10);
    pointLight.position.set(2, 3, 4);
    scene.add(pointLight);

    // ROOT POLYHEDRON GROUP
    const radarGroup = new THREE.Group();
    scene.add(radarGroup);

    // 1. Tetrahedral Solid Faces
    const vertices = new Float32Array([
      // Face 0: Top, Right, Left
      ...PILLAR_VERTICES[0], ...PILLAR_VERTICES[1], ...PILLAR_VERTICES[2],
      // Face 1: Top, Left, Back
      ...PILLAR_VERTICES[0], ...PILLAR_VERTICES[2], ...PILLAR_VERTICES[3],
      // Face 2: Top, Back, Right
      ...PILLAR_VERTICES[0], ...PILLAR_VERTICES[3], ...PILLAR_VERTICES[1],
      // Face 3: Bottom Base (Right, Back, Left)
      ...PILLAR_VERTICES[1], ...PILLAR_VERTICES[3], ...PILLAR_VERTICES[2],
    ]);

    const geom = new THREE.BufferGeometry();
    geom.setAttribute("position", new THREE.BufferAttribute(vertices, 3));
    geom.computeVertexNormals();

    const faceMat = new THREE.MeshStandardMaterial({
      color: 0x181e26,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.55,
      side: THREE.DoubleSide,
    });
    const solidMesh = new THREE.Mesh(geom, faceMat);
    radarGroup.add(solidMesh);

    // 2. Wireframe Outlines
    const wireMat = new THREE.LineBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.35,
    });
    const wireGeo = new THREE.WireframeGeometry(geom);
    const wireMesh = new THREE.LineSegments(wireGeo, wireMat);
    radarGroup.add(wireMesh);

    // 3. Center Origin Anchor & Axis lines
    const originGeo = new THREE.SphereGeometry(0.08, 16, 16);
    const originMat = new THREE.MeshBasicMaterial({ color: 0x737575 });
    const originMesh = new THREE.Mesh(originGeo, originMat);
    radarGroup.add(originMesh);

    PILLAR_VERTICES.forEach((vert) => {
      const axisPts = [new THREE.Vector3(0, 0, 0), new THREE.Vector3(...vert)];
      const axisLine = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(axisPts),
        new THREE.LineDashedMaterial({ color: 0x4a5568, opacity: 0.4, transparent: true, dashSize: 0.1, gapSize: 0.08 })
      );
      axisLine.computeLineDistances();
      radarGroup.add(axisLine);
    });

    // 4. Vertex Markers
    const vertexMeshes: THREE.Mesh[] = [];
    const markerGeo = new THREE.SphereGeometry(0.18, 20, 20);

    PILLAR_VERTICES.forEach((vert, idx) => {
      const mat = new THREE.MeshStandardMaterial({
        color: PILLAR_COLORS[idx],
        emissive: PILLAR_COLORS[idx],
        emissiveIntensity: 0.6,
        roughness: 0.2,
      });
      const marker = new THREE.Mesh(markerGeo, mat);
      marker.position.set(...vert);
      radarGroup.add(marker);
      vertexMeshes.push(marker);

      // Outer orbit halo ring
      const haloGeo = new THREE.RingGeometry(0.24, 0.29, 24);
      const haloMat = new THREE.MeshBasicMaterial({
        color: PILLAR_COLORS[idx],
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.5,
      });
      const haloMesh = new THREE.Mesh(haloGeo, haloMat);
      haloMesh.lookAt(camera.position);
      marker.add(haloMesh);
    });

    // Orbit coordinates per selected pillar
    const targetRotations = [
      { x: 0.1, y: 0 },              // Pillar 0 (Speed: Top Front)
      { x: 0.25, y: -Math.PI / 3 },   // Pillar 1 (Quality: Right Front)
      { x: 0.25, y: Math.PI / 3 },    // Pillar 2 (Integrity: Left Front)
      { x: -0.3, y: Math.PI },        // Pillar 3 (Retrieval: Back)
    ];

    let currentRotX = 0;
    let currentRotY = 0;
    let clock = new THREE.Clock();
    let animId: number;

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();
      const sIdx = selectedIndexRef.current;
      const target = targetRotations[sIdx] || targetRotations[0];

      // Smooth interpolation to target orientation
      const ease = 0.05;
      currentRotX += (target.x - currentRotX) * ease;
      currentRotY += (target.y - currentRotY) * ease;

      // Subtle breathing motion
      const wobble = shouldReduceMotion ? 0 : Math.sin(elapsedTime * 1.8) * 0.05;
      radarGroup.rotation.x = currentRotX + wobble;
      radarGroup.rotation.y = currentRotY;

      // Pulse selected vertex
      vertexMeshes.forEach((mesh, idx) => {
        if (idx === sIdx) {
          const pulse = 1.35 + Math.sin(elapsedTime * 5) * 0.2;
          mesh.scale.set(pulse, pulse, pulse);
          (mesh.material as THREE.MeshStandardMaterial).emissiveIntensity = 1.0;
        } else {
          mesh.scale.set(1.0, 1.0, 1.0);
          (mesh.material as THREE.MeshStandardMaterial).emissiveIntensity = 0.3;
        }
      });

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container || !renderer || !camera) return;
      const w = container.clientWidth || 320;
      const h = container.clientHeight || 260;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
      if (renderer.domElement.parentElement) {
        renderer.domElement.parentElement.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div className="relative w-full h-[220px] sm:h-[260px] flex items-center justify-center overflow-hidden rounded-xl bg-[#050607]/60 border border-[rgba(255,255,255,0.06)]">
      {/* 3D Canvas Mount */}
      <div ref={mountRef} className="w-full h-full" />

      {/* 3D HUD overlay badges */}
      <div className="absolute top-2.5 left-3 flex items-center gap-1.5 font-code text-[10px] text-[#737575] uppercase">
        <span className="w-1.5 h-1.5 rounded-full bg-[#FF4A16]" />
        <span>3D BENCHMARK RADAR</span>
      </div>

      <div className="absolute bottom-2.5 right-3 font-code text-[9px] text-[#8C9295] uppercase">
        TOPOLOGY: TETRAHEDRAL MANIFOLD
      </div>
    </div>
  );
}
