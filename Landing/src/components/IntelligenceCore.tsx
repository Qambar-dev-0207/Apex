"use client";

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";

interface IntelligenceCoreProps {
  scrollProgress?: number; // 0.0 to 1.0 (0: Hero, 0.33: Orchestration, 0.66: Execution, 1.0: Memory)
  className?: string;
  isHeroMode?: boolean; // When true, stays in hero configuration with parallax
}

export default function IntelligenceCore({
  scrollProgress = 0,
  className = "",
  isHeroMode = false,
}: IntelligenceCoreProps) {
  const mountRef = useRef<HTMLDivElement>(null);
  const [webglSupported, setWebglSupported] = useState(true);
  const [isLoaded, setIsLoaded] = useState(false);

  const progressRef = useRef(scrollProgress);
  const isHeroModeRef = useRef(isHeroMode);

  useEffect(() => {
    progressRef.current = scrollProgress;
    isHeroModeRef.current = isHeroMode;
  }, [scrollProgress, isHeroMode]);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // Check for WebGL support
    const canvasTest = document.createElement("canvas");
    const gl =
      canvasTest.getContext("webgl2") ||
      canvasTest.getContext("webgl") ||
      canvasTest.getContext("experimental-webgl");
    if (!gl) {
      setWebglSupported(false);
      return;
    }

    // Check prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // ─────────────────────────────────────────────────────────────
    // SCENE, CAMERA, RENDERER
    // ─────────────────────────────────────────────────────────────
    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || window.innerHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 100);
    camera.position.set(0, 0, 11);

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
      setIsLoaded(true);
    } catch {
      setWebglSupported(false);
      return;
    }

    // ─────────────────────────────────────────────────────────────
    // LIGHTING: Dark Titanium Aesthetics & Restrained Highlights
    // ─────────────────────────────────────────────────────────────
    const ambientLight = new THREE.AmbientLight(0x181e24, 1.4);
    scene.add(ambientLight);

    // Rim lights for razor-sharp specular metallic edges
    const rimLight1 = new THREE.DirectionalLight(0xb0c2d4, 2.4);
    rimLight1.position.set(8, 12, 10);
    scene.add(rimLight1);

    const rimLight2 = new THREE.DirectionalLight(0x4a5662, 1.6);
    rimLight2.position.set(-10, -8, -6);
    scene.add(rimLight2);

    // Subtle warm core accent point light
    const coreLight = new THREE.PointLight(0xff3700, 1.1, 14, 2.0);
    coreLight.position.set(0, 0, 0);
    scene.add(coreLight);

    // ─────────────────────────────────────────────────────────────
    // MATERIALS (Reused to prevent GPU churn)
    // ─────────────────────────────────────────────────────────────
    const titaniumMaterial = new THREE.MeshStandardMaterial({
      color: 0x181b1f,
      metalness: 0.9,
      roughness: 0.25,
    });

    const edgeLineMaterial = new THREE.LineBasicMaterial({
      color: 0xdde5e8,
      transparent: true,
      opacity: 0.28,
    });

    const subtleLineMaterial = new THREE.LineBasicMaterial({
      color: 0x7e8b93,
      transparent: true,
      opacity: 0.14,
    });

    const orangeAccentMaterial = new THREE.MeshBasicMaterial({
      color: 0xff3700,
    });

    const orangeLineMaterial = new THREE.LineBasicMaterial({
      color: 0xff3700,
      transparent: true,
      opacity: 0.85,
    });

    const whiteNodeMaterial = new THREE.MeshStandardMaterial({
      color: 0xf3f4f2,
      metalness: 0.9,
      roughness: 0.18,
    });

    // ─────────────────────────────────────────────────────────────
    // ROOT ASSEMBLY GROUP
    // ─────────────────────────────────────────────────────────────
    const rootAssembly = new THREE.Group();
    scene.add(rootAssembly);

    // 1. Central Dark Polyhedral Core (Obsidian/Titanium Icosahedron)
    const coreGeometry = new THREE.IcosahedronGeometry(0.85, 0);
    const coreMesh = new THREE.Mesh(coreGeometry, titaniumMaterial);
    rootAssembly.add(coreMesh);

    // Core Wireframe outline
    const coreWireGeometry = new THREE.WireframeGeometry(coreGeometry);
    const coreWire = new THREE.LineSegments(coreWireGeometry, edgeLineMaterial);
    coreMesh.add(coreWire);

    // Inner glowing heart dot
    const heartMesh = new THREE.Mesh(new THREE.SphereGeometry(0.12, 16, 16), orangeAccentMaterial);
    coreMesh.add(heartMesh);

    // 2. The 24-Layer Structural Assembly
    interface RingLayer {
      group: THREE.Group;
      baseRadius: number;
      baseRotX: number;
      baseRotY: number;
      baseRotZ: number;
      speedRotY: number;
      speedRotX: number;
      dagTargetPos: THREE.Vector3;
      dagTargetRot: THREE.Euler;
      execTargetPos: THREE.Vector3;
      execTargetRot: THREE.Euler;
      memTargetPos: THREE.Vector3;
      memTargetRot: THREE.Euler;
    }

    const ringLayers: RingLayer[] = [];
    const ringGroup = new THREE.Group();
    rootAssembly.add(ringGroup);

    const nodeSphereGeom = new THREE.SphereGeometry(0.045, 12, 12);
    const orangeNodeSphereGeom = new THREE.SphereGeometry(0.065, 12, 12);

    for (let i = 0; i < 24; i++) {
      const layerGroup = new THREE.Group();
      const radius = 1.25 + i * 0.145; // Radius from 1.25 to ~4.6
      const segments = 48 + (i % 5) * 8;
      const angleSpan = Math.PI * 2 * (0.45 + (i % 7) * 0.08); // Segmented arcs with deliberate gaps
      const startAngle = (i * 0.42) % (Math.PI * 2);

      const curve = new THREE.EllipseCurve(0, 0, radius, radius, startAngle, startAngle + angleSpan, false, 0);
      const points = curve.getPoints(segments);
      const arcGeometry = new THREE.BufferGeometry().setFromPoints(points);

      const isKeyTier = i === 3 || i === 9 || i === 15 || i === 21; // 4 Key architectural tier rings
      const lineMat = isKeyTier ? edgeLineMaterial : subtleLineMaterial;
      const ringLine = new THREE.Line(arcGeometry, lineMat);
      layerGroup.add(ringLine);

      // Add small precision tick nodes along selected ring points
      if (i % 3 === 0) {
        const tickCount = 2 + (i % 3);
        for (let t = 0; t < tickCount; t++) {
          const ptIdx = Math.floor((points.length / (tickCount + 1)) * (t + 1));
          if (points[ptIdx]) {
            const isOrangeMarker = (i === 9 && t === 0) || (i === 15 && t === 1);
            const marker = new THREE.Mesh(
              isOrangeMarker ? orangeNodeSphereGeom : nodeSphereGeom,
              isOrangeMarker ? orangeAccentMaterial : whiteNodeMaterial
            );
            marker.position.set(points[ptIdx].x, points[ptIdx].y, 0);
            layerGroup.add(marker);
          }
        }
      }

      // Initial sovereign spherical/elliptical inclinations
      const rotX = i * 0.17 - 1.2;
      const rotY = i * 0.23;
      const rotZ = i * 0.09 - 0.4;
      layerGroup.rotation.set(rotX, rotY, rotZ);

      // Target transforms for the 3 ScrollStory stages:
      // State 01: DAG plan orientation (aligned along X with ordered layer offsets)
      const dagPos = new THREE.Vector3((i - 12) * 0.16, Math.sin(i * 0.5) * 0.3, ((i % 3) - 1) * 0.15);
      const dagRot = new THREE.Euler(0.2, i * 0.05, 0);

      // State 02: Execution conduits (parallel streaming horizontal channels)
      const conduitLane = (i % 3) - 1; // -1, 0, 1
      const execPos = new THREE.Vector3(
        ((i % 8) - 4) * 0.52,
        conduitLane * 1.35 + Math.sin(i * 0.8) * 0.12,
        Math.cos(i * 0.5) * 0.35
      );
      const execRot = new THREE.Euler(0.4 * conduitLane, 0.3, 0.1);

      // State 03: Memory clusters (two compact orbital manifolds: Redis & ChromaDB)
      const isRedisCluster = i % 2 === 0;
      const clusterCenter = isRedisCluster ? new THREE.Vector3(-1.3, 0.2, 0) : new THREE.Vector3(1.3, -0.2, 0);
      const memRadius = 0.5 + (i % 6) * 0.16;
      const memAngle = i * 0.6;
      const memPos = new THREE.Vector3(
        clusterCenter.x + Math.cos(memAngle) * memRadius,
        clusterCenter.y + Math.sin(memAngle) * memRadius,
        clusterCenter.z + ((i % 4) - 2) * 0.15
      );
      const memRot = new THREE.Euler(rotX * 0.6, rotY * 0.6, rotZ * 0.6);

      ringGroup.add(layerGroup);
      ringLayers.push({
        group: layerGroup,
        baseRadius: radius,
        baseRotX: rotX,
        baseRotY: rotY,
        baseRotZ: rotZ,
        speedRotY: 0.0007 + (i % 4) * 0.0003,
        speedRotX: 0.0003 + (i % 3) * 0.0002,
        dagTargetPos: dagPos,
        dagTargetRot: dagRot,
        execTargetPos: execPos,
        execTargetRot: execRot,
        memTargetPos: memPos,
        memTargetRot: memRot,
      });
    }

    // 3. Four Major Architectural Tier Orbital Guides (Strategy, Context, Muscle, HUD)
    const orbitalGroup = new THREE.Group();
    rootAssembly.add(orbitalGroup);
    const orbitalRadii = [2.1, 2.9, 3.7, 4.4];
    const orbitalTilts = [
      { x: 0.5, y: 0.2, z: 0.1 },
      { x: -0.4, y: 0.8, z: -0.2 },
      { x: 0.7, y: -0.5, z: 0.3 },
      { x: -0.2, y: 1.1, z: 0.5 },
    ];

    orbitalRadii.forEach((r, idx) => {
      const orbCurve = new THREE.EllipseCurve(0, 0, r, r, 0, Math.PI * 2, false, 0);
      const orbPts = orbCurve.getPoints(96);
      const orbGeom = new THREE.BufferGeometry().setFromPoints(orbPts);
      const orbLine = new THREE.Line(orbGeom, edgeLineMaterial);
      orbLine.rotation.set(orbitalTilts[idx].x, orbitalTilts[idx].y, orbitalTilts[idx].z);
      orbitalGroup.add(orbLine);
    });

    // 4. DAG & Execution Dependency Nodes
    const graphGroup = new THREE.Group();
    rootAssembly.add(graphGroup);

    interface StoryNode {
      mesh: THREE.Mesh;
      basePos: THREE.Vector3;
      dagPos: THREE.Vector3;
      execPos: THREE.Vector3;
      memPos: THREE.Vector3;
      isOrange?: boolean;
    }

    const storyNodes: StoryNode[] = [];
    const nodeCoords = [
      // Node 0: Root Intent
      { base: [0, 0, 0], dag: [-2.6, 0, 0], exec: [-2.6, 0, 0], mem: [-1.4, 0, 0], orange: true },
      // Node 1: Socratic Decomposition
      { base: [0.8, 0.6, 0.4], dag: [-1.4, 0.9, 0], exec: [-1.4, 1.2, 0.3], mem: [-1.1, 0.6, 0.2] },
      // Node 2: Intent Classification
      { base: [-0.7, 0.5, -0.5], dag: [-1.4, 0, 0], exec: [-1.4, 0, 0], mem: [-1.6, -0.4, 0.1] },
      // Node 3: AST Symbol Extractor
      { base: [0.5, -0.8, 0.3], dag: [-1.4, -0.9, 0], exec: [-1.4, -1.2, -0.3], mem: [-0.9, -0.5, -0.2] },
      // Node 4: Task DAG Branch A (Web Swarm)
      { base: [-1.1, -0.4, 0.6], dag: [0.1, 1.3, 0], exec: [0.0, 1.4, 0.4], mem: [1.0, 0.7, 0.2] },
      // Node 5: Task DAG Branch B (Code Engine)
      { base: [1.2, -0.2, -0.4], dag: [0.1, 0, 0], exec: [0.0, 0, 0], mem: [1.4, 0.1, 0], orange: true },
      // Node 6: Task DAG Branch C (Sandbox Exec)
      { base: [-0.6, 1.1, 0.2], dag: [0.1, -1.3, 0], exec: [0.0, -1.4, -0.4], mem: [1.1, -0.7, -0.2] },
      // Node 7: Convergence Verification Gate
      { base: [1.4, 0.8, -0.2], dag: [1.6, 0.6, 0], exec: [1.5, 0.7, 0.2], mem: [1.6, 0.4, 0.1] },
      // Node 8: Output Validation
      { base: [-0.3, -1.3, -0.5], dag: [1.6, -0.6, 0], exec: [1.5, -0.7, -0.2], mem: [0.7, -0.2, 0.2] },
      // Node 9: Final Verified Commit
      { base: [1.8, 0, 0.2], dag: [2.7, 0, 0], exec: [2.7, 0, 0], mem: [1.8, -0.1, 0], orange: true },
    ];

    nodeCoords.forEach((coord) => {
      const geom = new THREE.SphereGeometry(coord.orange ? 0.08 : 0.055, 14, 14);
      const mat = coord.orange ? orangeAccentMaterial : whiteNodeMaterial;
      const mesh = new THREE.Mesh(geom, mat);
      mesh.position.set(coord.base[0], coord.base[1], coord.base[2]);
      graphGroup.add(mesh);

      storyNodes.push({
        mesh,
        basePos: new THREE.Vector3(...coord.base),
        dagPos: new THREE.Vector3(...coord.dag),
        execPos: new THREE.Vector3(...coord.exec),
        memPos: new THREE.Vector3(...coord.mem),
        isOrange: coord.orange,
      });
    });

    const dependencyPairs: [number, number][] = [
      [0, 1],
      [0, 2],
      [0, 3],
      [1, 4],
      [2, 5],
      [3, 6],
      [4, 7],
      [5, 7],
      [5, 8],
      [6, 8],
      [7, 9],
      [8, 9],
    ];

    const lineGeom = new THREE.BufferGeometry();
    const linePositions = new Float32Array(dependencyPairs.length * 2 * 3);
    lineGeom.setAttribute("position", new THREE.BufferAttribute(linePositions, 3));
    const dynamicLines = new THREE.LineSegments(lineGeom, edgeLineMaterial);
    graphGroup.add(dynamicLines);

    // Orange Convergence Highlight Line (active in Execution)
    const orangeLineGeom = new THREE.BufferGeometry();
    const orangeLinePos = new Float32Array(4 * 3);
    orangeLineGeom.setAttribute("position", new THREE.BufferAttribute(orangeLinePos, 3));
    const orangeConvergenceLines = new THREE.LineSegments(orangeLineGeom, orangeLineMaterial);
    graphGroup.add(orangeConvergenceLines);

    // ─────────────────────────────────────────────────────────────
    // POINTER PARALLAX
    // ─────────────────────────────────────────────────────────────
    const mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };

    const handleMouseMove = (e: MouseEvent) => {
      if (prefersReducedMotion) return;
      const rect = container.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -(((e.clientY - rect.top) / rect.height) * 2 - 1);
      mouse.targetX = Math.max(-1, Math.min(1, x));
      mouse.targetY = Math.max(-1, Math.min(1, y));
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth || window.innerWidth;
      const h = container.clientHeight || window.innerHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener("resize", handleResize);

    let isTabVisible = !document.hidden;
    const handleVisibility = () => {
      isTabVisible = !document.hidden;
    };
    document.addEventListener("visibilitychange", handleVisibility);

    // ─────────────────────────────────────────────────────────────
    // ANIMATION LOOP
    // ─────────────────────────────────────────────────────────────
    let animationFrameId: number;
    let lastTime = performance.now();

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      if (!isTabVisible) return;

      const now = performance.now();
      const delta = Math.min((now - lastTime) / 1000, 0.1);
      lastTime = now;

      mouse.x += (mouse.targetX - mouse.x) * 0.04;
      mouse.y += (mouse.targetY - mouse.y) * 0.04;

      const currentProg = progressRef.current;
      const isHero = isHeroModeRef.current;
      const isDesktop = (container.clientWidth || window.innerWidth) >= 1024;
      const isMobile = (container.clientWidth || window.innerWidth) < 768;

      if (isHero) {
        // Desktop: Center-Right. Mobile: Scaled down & positioned gracefully
        const targetX = isDesktop ? 1.85 : 0;
        const targetY = isDesktop ? 0.05 : (isMobile ? 0.85 : 0.4);
        rootAssembly.position.x += (targetX - rootAssembly.position.x) * 0.05;
        rootAssembly.position.y += (targetY - rootAssembly.position.y) * 0.05;
        rootAssembly.scale.setScalar(isDesktop ? 1.05 : (isMobile ? 0.65 : 0.8));
      } else {
        // Story Mode: Center-Right for desktop reading area, centered for mobile
        const targetX = isDesktop ? 1.45 : 0;
        const targetY = isDesktop ? 0 : (isMobile ? 0.9 : 0.5);
        rootAssembly.position.x += (targetX - rootAssembly.position.x) * 0.05;
        rootAssembly.position.y += (targetY - rootAssembly.position.y) * 0.05;
        rootAssembly.scale.setScalar(isDesktop ? 0.95 : (isMobile ? 0.62 : 0.75));
      }

      if (!prefersReducedMotion) {
        rootAssembly.rotation.y = mouse.x * 0.2;
        rootAssembly.rotation.x = -mouse.y * 0.14;
      }

      if (!prefersReducedMotion) {
        coreMesh.rotation.y += 0.002;
        coreMesh.rotation.x += 0.001;
        orbitalGroup.rotation.y -= 0.0006;
      }

      const prog = Math.max(0, Math.min(1, currentProg));

      let t1 = 0;
      let t2 = 0;
      let t3 = 0;

      if (prog <= 0.33) {
        t1 = prog / 0.33;
      } else if (prog <= 0.66) {
        t1 = 1.0;
        t2 = (prog - 0.33) / 0.33;
      } else {
        t1 = 1.0;
        t2 = 1.0;
        t3 = (prog - 0.66) / 0.34;
      }

      // Interpolate the 24 ring layers
      ringLayers.forEach((rl) => {
        if (!prefersReducedMotion) {
          rl.baseRotY += rl.speedRotY;
          rl.baseRotX += rl.speedRotX;
        }

        let curTargetPos = new THREE.Vector3(0, 0, 0);
        let curTargetRot = new THREE.Euler(rl.baseRotX, rl.baseRotY, rl.baseRotZ);

        if (t1 > 0 && t2 === 0) {
          curTargetPos.lerpVectors(new THREE.Vector3(0, 0, 0), rl.dagTargetPos, t1);
          curTargetRot.x = THREE.MathUtils.lerp(rl.baseRotX, rl.dagTargetRot.x, t1);
          curTargetRot.y = THREE.MathUtils.lerp(rl.baseRotY, rl.dagTargetRot.y, t1);
          curTargetRot.z = THREE.MathUtils.lerp(rl.baseRotZ, rl.dagTargetRot.z, t1);
        } else if (t2 > 0 && t3 === 0) {
          curTargetPos.lerpVectors(rl.dagTargetPos, rl.execTargetPos, t2);
          curTargetRot.x = THREE.MathUtils.lerp(rl.dagTargetRot.x, rl.execTargetRot.x, t2);
          curTargetRot.y = THREE.MathUtils.lerp(rl.dagTargetRot.y, rl.execTargetRot.y, t2);
          curTargetRot.z = THREE.MathUtils.lerp(rl.dagTargetRot.z, rl.execTargetRot.z, t2);
        } else if (t3 > 0) {
          curTargetPos.lerpVectors(rl.execTargetPos, rl.memTargetPos, t3);
          curTargetRot.x = THREE.MathUtils.lerp(rl.execTargetRot.x, rl.memTargetRot.x, t3);
          curTargetRot.y = THREE.MathUtils.lerp(rl.execTargetRot.y, rl.memTargetRot.y, t3);
          curTargetRot.z = THREE.MathUtils.lerp(rl.execTargetRot.z, rl.memTargetRot.z, t3);
        }

        rl.group.position.lerp(curTargetPos, 0.08);
        rl.group.rotation.x = THREE.MathUtils.lerp(rl.group.rotation.x, curTargetRot.x, 0.08);
        rl.group.rotation.y = THREE.MathUtils.lerp(rl.group.rotation.y, curTargetRot.y, 0.08);
        rl.group.rotation.z = THREE.MathUtils.lerp(rl.group.rotation.z, curTargetRot.z, 0.08);
      });

      // Interpolate Story Nodes
      storyNodes.forEach((node) => {
        let nodeTarget = new THREE.Vector3();

        if (t1 === 0) {
          nodeTarget.copy(node.basePos);
        } else if (t1 > 0 && t2 === 0) {
          nodeTarget.lerpVectors(node.basePos, node.dagPos, t1);
        } else if (t2 > 0 && t3 === 0) {
          nodeTarget.lerpVectors(node.dagPos, node.execPos, t2);
        } else {
          nodeTarget.lerpVectors(node.execPos, node.memPos, t3);
        }

        node.mesh.position.lerp(nodeTarget, 0.09);
      });

      // Update dynamic connecting line vertices
      const posAttr = lineGeom.getAttribute("position") as THREE.BufferAttribute;
      const posArray = posAttr.array as Float32Array;

      dependencyPairs.forEach((pair, idx) => {
        const p1 = storyNodes[pair[0]].mesh.position;
        const p2 = storyNodes[pair[1]].mesh.position;
        const baseIdx = idx * 6;
        posArray[baseIdx + 0] = p1.x;
        posArray[baseIdx + 1] = p1.y;
        posArray[baseIdx + 2] = p1.z;
        posArray[baseIdx + 3] = p2.x;
        posArray[baseIdx + 4] = p2.y;
        posArray[baseIdx + 5] = p2.z;
      });
      posAttr.needsUpdate = true;

      // Update orange convergence lines
      const orangeAttr = orangeLineGeom.getAttribute("position") as THREE.BufferAttribute;
      const orangeArray = orangeAttr.array as Float32Array;
      const n7 = storyNodes[7].mesh.position;
      const n8 = storyNodes[8].mesh.position;
      const n9 = storyNodes[9].mesh.position;
      orangeArray[0] = n7.x;
      orangeArray[1] = n7.y;
      orangeArray[2] = n7.z;
      orangeArray[3] = n9.x;
      orangeArray[4] = n9.y;
      orangeArray[5] = n9.z;
      orangeArray[6] = n8.x;
      orangeArray[7] = n8.y;
      orangeArray[8] = n8.z;
      orangeArray[9] = n9.x;
      orangeArray[10] = n9.y;
      orangeArray[11] = n9.z;
      orangeAttr.needsUpdate = true;

      const lineOpacity = isHero ? 0.15 : THREE.MathUtils.lerp(0.2, 0.45, Math.min(1, prog * 2));
      edgeLineMaterial.opacity = lineOpacity;
      orangeLineMaterial.opacity = t2 > 0.3 ? 0.9 : 0.0;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("resize", handleResize);
      document.removeEventListener("visibilitychange", handleVisibility);

      coreGeometry.dispose();
      coreWireGeometry.dispose();
      nodeSphereGeom.dispose();
      orangeNodeSphereGeom.dispose();
      lineGeom.dispose();
      orangeLineGeom.dispose();

      titaniumMaterial.dispose();
      edgeLineMaterial.dispose();
      subtleLineMaterial.dispose();
      orangeAccentMaterial.dispose();
      orangeLineMaterial.dispose();
      whiteNodeMaterial.dispose();

      renderer.dispose();
      if (renderer.domElement && renderer.domElement.parentNode) {
        renderer.domElement.parentNode.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div className={`relative w-full h-full pointer-events-none select-none ${className}`}>
      <div ref={mountRef} className="absolute inset-0 w-full h-full" />

      {(!isLoaded || !webglSupported) && (
        <div
          className="absolute inset-0 flex items-center justify-center pointer-events-none transition-opacity duration-700"
          style={{ opacity: isLoaded ? 0 : 1 }}
          aria-hidden="true"
        >
          <svg
            viewBox="0 0 400 400"
            className="w-[85%] max-w-[500px] h-auto text-[rgba(235,240,238,0.22)]"
            fill="none"
          >
            <circle cx="200" cy="200" r="160" stroke="currentColor" strokeWidth="1" strokeDasharray="6 4" />
            <circle cx="200" cy="200" r="130" stroke="currentColor" strokeWidth="0.8" />
            <circle cx="200" cy="200" r="100" stroke="currentColor" strokeWidth="1.2" strokeDasharray="18 12" />
            <circle cx="200" cy="200" r="70" stroke="currentColor" strokeWidth="0.8" />
            <circle cx="200" cy="200" r="40" stroke="currentColor" strokeWidth="1" />
            <line x1="20" y1="200" x2="380" y2="200" stroke="currentColor" strokeWidth="0.6" strokeDasharray="3 3" />
            <line x1="200" y1="20" x2="200" y2="380" stroke="currentColor" strokeWidth="0.6" strokeDasharray="3 3" />
            <polygon
              points="200,165 230,185 230,215 200,235 170,215 170,185"
              stroke="#F3F4F2"
              strokeWidth="1.2"
              fill="#111315"
            />
            <circle cx="200" cy="200" r="4" fill="#FF3700" />
            <circle cx="200" cy="200" r="12" stroke="#FF3700" strokeWidth="0.8" opacity="0.4" />
          </svg>
        </div>
      )}
    </div>
  );
}
