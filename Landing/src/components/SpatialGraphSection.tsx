w"use client";

import React, { useEffect, useRef, useState, useId } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import * as THREE from "three";
import {
  Share2,
  GitFork,
  Activity,
  RotateCw,
  Maximize2,
  ZoomIn,
  ZoomOut,
  Info,
  Layers,
  Sparkles,
  CheckCircle2,
  Cpu,
  Database,
  Shield,
  Workflow,
} from "lucide-react";
import { MOTION_EASE } from "../lib/motion";

export type GraphMode = "memory" | "dag" | "pareto";

interface GraphNodeData {
  id: string;
  name: string;
  category: string;
  layer: string;
  cluster: string;
  latency: string;
  status: string;
  description: string;
  coordinates: [number, number, number];
  color: number;
}

const MEMORY_NODES: GraphNodeData[] = [
  // Cluster A: AST Code Graph (Amber)
  {
    id: "ast-01",
    name: "AST::SymbolParser",
    category: "Code Intelligence",
    layer: "L12 AST Compression",
    cluster: "AST Symbol Index",
    latency: "5.75 ms",
    status: "INDEXED",
    description: "Tree-sitter AST symbol extractor mapping definitions, function signatures, and call references.",
    coordinates: [-3.2, 1.8, 0.8],
    color: 0xffaa00,
  },
  {
    id: "ast-02",
    name: "AST::CallGraph",
    category: "Code Intelligence",
    layer: "L12 AST Compression",
    cluster: "AST Symbol Index",
    latency: "3.20 ms",
    status: "RESOLVED",
    description: "Topological caller-callee dependency resolution graph preventing hallucinated import paths.",
    coordinates: [-2.4, 2.8, -0.6],
    color: 0xffaa00,
  },
  {
    id: "ast-03",
    name: "AST::ScopeResolver",
    category: "Code Intelligence",
    layer: "L12 AST Compression",
    cluster: "AST Symbol Index",
    latency: "2.10 ms",
    status: "SYNCED",
    description: "Lexical scope analyzer guaranteeing deterministic variable bindings during code editing.",
    coordinates: [-4.0, 0.8, -0.2],
    color: 0xffaa00,
  },

  // Cluster B: ChromaDB Latent Vectors (Violet / Indigo)
  {
    id: "vec-01",
    name: "ChromaDB::D1536",
    category: "Vector Retrieval",
    layer: "L6 Semantic Memory",
    cluster: "Latent Space D=1536",
    latency: "14.2 ms",
    status: "RETRIEVED",
    description: "High-dimensional embedding store with HNSW index indexing project documentation and memory.",
    coordinates: [3.4, 1.6, -1.2],
    color: 0xa855f7,
  },
  {
    id: "vec-02",
    name: "CosineSim::NearestK",
    category: "Vector Retrieval",
    layer: "L6 Semantic Memory",
    cluster: "Latent Space D=1536",
    latency: "8.60 ms",
    status: "RECALLED",
    description: "Cosine similarity ranker achieving Recall@3 = 1.0 and MRR = 1.0 across canonical queries.",
    coordinates: [2.6, 2.7, 0.4],
    color: 0xa855f7,
  },
  {
    id: "vec-03",
    name: "Vector::ContextInjector",
    category: "Vector Retrieval",
    layer: "L6 Semantic Memory",
    cluster: "Latent Space D=1536",
    latency: "4.15 ms",
    status: "PRIMED",
    description: "Dynamic context window packer injecting top semantic chunks into prompt prefix.",
    coordinates: [4.2, 0.5, 0.2],
    color: 0xa855f7,
  },

  // Cluster C: Episodic Working Memory (Cyan / Teal)
  {
    id: "mem-01",
    name: "Redis::WorkingState",
    category: "Working Memory",
    layer: "L5 Hot State",
    cluster: "Hot Working Context",
    latency: "0.85 ms",
    status: "ACTIVE",
    description: "Sub-millisecond persistent in-memory session log holding current multi-turn dialogue state.",
    coordinates: [-1.2, -2.4, 1.4],
    color: 0x06b6d4,
  },
  {
    id: "mem-02",
    name: "Episodic::TimelineBuffer",
    category: "Working Memory",
    layer: "L5 Hot State",
    cluster: "Hot Working Context",
    latency: "1.12 ms",
    status: "RECORDING",
    description: "Sliding window of user interactions, tool feedback loops, and environment observations.",
    coordinates: [-2.2, -1.6, 2.2],
    color: 0x06b6d4,
  },
  {
    id: "mem-03",
    name: "AgentHarness::Checkpoint",
    category: "Working Memory",
    layer: "L7 Sandboxing",
    cluster: "Hot Working Context",
    latency: "0.04 ms",
    status: "SNAPSHOT",
    description: "Bit-for-bit SHA256 snapshot for atomic rollbacks if validation rules fail.",
    coordinates: [-0.4, -3.2, 0.4],
    color: 0x06b6d4,
  },

  // Cluster D: Socratic Verification (Apex Vermilion / Orange)
  {
    id: "soc-01",
    name: "Socratic::SteelmanProof",
    category: "Verification",
    layer: "L15 Socratic Gate",
    cluster: "Socratic Rule Engine",
    latency: "42.0 ms",
    status: "VERIFIED",
    description: "Counter-thesis reasoning engine probing blind spots before code mutation approval.",
    coordinates: [1.8, -2.2, -1.5],
    color: 0xff4a16,
  },
  {
    id: "soc-02",
    name: "Rule::ProtectedShield",
    category: "Verification",
    layer: "L7 Sandboxing",
    cluster: "Socratic Rule Engine",
    latency: "0.01 ms",
    status: "SHIELDED",
    description: "Zero-latency guardrail blocking path traversal (../) and protected system credentials (.env).",
    coordinates: [2.8, -1.4, -2.4],
    color: 0xff4a16,
  },
  {
    id: "soc-03",
    name: "Diff::IntegrityAudit",
    category: "Verification",
    layer: "L16 Self-Correction",
    cluster: "Socratic Rule Engine",
    latency: "6.30 ms",
    status: "AUDITED",
    description: "AST-level diff comparator guaranteeing no syntax errors or breaking changes are introduced.",
    coordinates: [0.8, -3.0, -0.8],
    color: 0xff4a16,
  },
];

const DAG_NODES: GraphNodeData[] = [
  // Tier 0: Root Intent
  {
    id: "dag-00",
    name: "DirectIntent::Ingress",
    category: "Ingress Pipeline",
    layer: "L1 Ingestion",
    cluster: "Tier 0 — Ingestion",
    latency: "0.003 ms",
    status: "CLASSIFIED",
    description: "Deterministic regex scout and intent classifier skipping LLM latency on cached paths.",
    coordinates: [0, 3.6, 0],
    color: 0xf5f3ef,
  },

  // Tier 1: Master Orchestration Planner
  {
    id: "dag-01",
    name: "Gemini 3.8 Flash // Planner",
    category: "Master Orchestration",
    layer: "L3 Task Planning",
    cluster: "Tier 1 — Master Orchestrator",
    latency: "185 ms",
    status: "DISPATCHED",
    description: "Decomposes complex objectives into a mathematically acyclic dependency DAG with parallel threads.",
    coordinates: [0, 2.0, 0],
    color: 0xff4a16,
  },

  // Tier 2: Parallel Swarm Execution Lanes
  {
    id: "dag-02a",
    name: "Lane α // CodeCompass AST",
    category: "Parallel Worker",
    layer: "L12 AST Intelligence",
    cluster: "Tier 2 — Parallel Swarm",
    latency: "5.75 ms",
    status: "COMPLETED",
    description: "Parses target symbols and generates localized syntax diff with zero context hallucination.",
    coordinates: [-3.4, 0.2, 0.8],
    color: 0xffaa00,
  },
  {
    id: "dag-02b",
    name: "Lane β // Vector Knowledge",
    category: "Parallel Worker",
    layer: "L6 Vector Memory",
    cluster: "Tier 2 — Parallel Swarm",
    latency: "14.2 ms",
    status: "COMPLETED",
    description: "Retrieves architectural invariants and past session patterns from ChromaDB collection.",
    coordinates: [-1.2, 0.4, -0.6],
    color: 0xa855f7,
  },
  {
    id: "dag-02c",
    name: "Lane γ // Web Documentation",
    category: "Parallel Worker",
    layer: "L11 Web Grounding",
    cluster: "Tier 2 — Parallel Swarm",
    latency: "320 ms",
    status: "COMPLETED",
    description: "Fetches live API signatures, changelogs, and SDK specifications via DuckDuckGo & OpenAlex.",
    coordinates: [1.2, 0.4, -0.6],
    color: 0x06b6d4,
  },
  {
    id: "dag-02d",
    name: "Lane δ // Subagent Tool Harness",
    category: "Parallel Worker",
    layer: "L14 Autonomous Agent",
    cluster: "Tier 2 — Parallel Swarm",
    latency: "45.0 ms",
    status: "COMPLETED",
    description: "Executes sandboxed system operations with rollback safeguards across 35 AgentHarness tools.",
    coordinates: [3.4, 0.2, 0.8],
    color: 0x10b981,
  },

  // Tier 3: Validation & Socratic Critique
  {
    id: "dag-03a",
    name: "Socratic Critic // Gemini 3.1 Pro",
    category: "Verification",
    layer: "L15 Socratic Gate",
    cluster: "Tier 3 — Verification Gate",
    latency: "410 ms",
    status: "VERIFIED",
    description: "Challenges proposed modifications, checks edge cases, and enforces strict architectural integrity.",
    coordinates: [-1.6, -1.8, 0],
    color: 0xe9d0ad,
  },
  {
    id: "dag-03b",
    name: "Security Sandbox // SHA256 Diff",
    category: "Verification",
    layer: "L7 Sandboxing",
    cluster: "Tier 3 — Verification Gate",
    latency: "0.08 ms",
    status: "SHIELDED",
    description: "Verifies hashes against atomic checkpoint before committal to filesystem.",
    coordinates: [1.6, -1.8, 0],
    color: 0x10b981,
  },

  // Tier 4: Output Synthesis & Committal
  {
    id: "dag-04",
    name: "ResponseAssembler // Telemetry Commit",
    category: "Delivery",
    layer: "L24 Sovereign Assembly",
    cluster: "Tier 4 — Synthesis",
    latency: "1.20 ms",
    status: "COMMITTED",
    description: "Renders stream to user terminal, saves telemetry metrics, and commits episodic memory.",
    coordinates: [0, -3.4, 0],
    color: 0xff4a16,
  },
];

export default function SpatialGraphSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasWrapperRef = useRef<HTMLDivElement>(null);
  const shouldReduceMotion = useReducedMotion();

  const [activeMode, setActiveMode] = useState<GraphMode>("memory");
  const [selectedNode, setSelectedNode] = useState<GraphNodeData | null>(MEMORY_NODES[0]);
  const [isAutoRotate, setIsAutoRotate] = useState<boolean>(true);
  const [webglSupported, setWebglSupported] = useState<boolean>(true);
  const [mouseCoords, setMouseCoords] = useState<{ x: string; y: string; z: string }>({
    x: "+0.00",
    y: "+0.00",
    z: "+0.00",
  });
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  // References to keep Three.js resources clean & smooth
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const graphGroupRef = useRef<THREE.Group | null>(null);
  const paretoMeshRef = useRef<THREE.Mesh | null>(null);
  const paretoBeaconRef = useRef<THREE.Group | null>(null);
  const pulseParticlesRef = useRef<THREE.Points | null>(null);
  const activeNodesRef = useRef<GraphNodeData[]>(MEMORY_NODES);
  const interactiveMeshesRef = useRef<THREE.Mesh[]>([]);
  const hoverRingRef = useRef<THREE.Mesh | null>(null);
  const animationFrameIdRef = useRef<number | null>(null);

  // Orbit state
  const orbitState = useRef({
    isDragging: false,
    prevX: 0,
    prevY: 0,
    rotX: 0.25,
    rotY: -0.35,
    targetRotX: 0.25,
    targetRotY: -0.35,
    zoom: 11,
    targetZoom: 11,
  });

  const uniqueId = useId();

  // Switch node data when mode changes
  useEffect(() => {
    if (activeMode === "memory") {
      activeNodesRef.current = MEMORY_NODES;
      setSelectedNode(MEMORY_NODES[0]);
    } else if (activeMode === "dag") {
      activeNodesRef.current = DAG_NODES;
      setSelectedNode(DAG_NODES[1]); // Gemini 3.8 Flash
    } else {
      activeNodesRef.current = [];
      setSelectedNode(null);
    }
    rebuildGraphScene();
  }, [activeMode]);

  // Main Three.js Initialization
  useEffect(() => {
    const container = canvasWrapperRef.current;
    if (!container) return;

    // Test WebGL support
    const testCanvas = document.createElement("canvas");
    const gl =
      testCanvas.getContext("webgl2") ||
      testCanvas.getContext("webgl") ||
      testCanvas.getContext("experimental-webgl");
    if (!gl) {
      setWebglSupported(false);
      return;
    }

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 560;

    // SCENE & CAMERA
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
    camera.position.set(0, 0, orbitState.current.zoom);
    cameraRef.current = camera;

    // RENDERER
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
      rendererRef.current = renderer;
      container.appendChild(renderer.domElement);
    } catch {
      setWebglSupported(false);
      return;
    }

    // LIGHTING
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xff4a16, 2.5);
    dirLight1.position.set(10, 15, 10);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x38bdf8, 1.8);
    dirLight2.position.set(-10, -10, -8);
    scene.add(dirLight2);

    // Root Graph Group
    const graphGroup = new THREE.Group();
    scene.add(graphGroup);
    graphGroupRef.current = graphGroup;

    // Hover Highlight Ring
    const ringGeo = new THREE.RingGeometry(0.36, 0.44, 32);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0,
    });
    const hoverRing = new THREE.Mesh(ringGeo, ringMat);
    scene.add(hoverRing);
    hoverRingRef.current = hoverRing;

    // Initial Scene Build
    rebuildGraphScene();

    // ─────────────────────────────────────────────────────────────
    // INTERACTION LISTENERS (Orbit, Drag, Zoom, Raycast)
    // ─────────────────────────────────────────────────────────────
    const dom = renderer.domElement;
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onPointerDown = (e: PointerEvent) => {
      orbitState.current.isDragging = true;
      orbitState.current.prevX = e.clientX;
      orbitState.current.prevY = e.clientY;
      dom.setPointerCapture(e.pointerId);
    };

    const onPointerMove = (e: PointerEvent) => {
      const rect = dom.getBoundingClientRect();
      const clientX = e.clientX - rect.left;
      const clientY = e.clientY - rect.top;

      // Update normalized device coordinates for Raycasting
      mouse.x = (clientX / rect.width) * 2 - 1;
      mouse.y = -(clientY / rect.height) * 2 + 1;

      if (orbitState.current.isDragging) {
        const dx = e.clientX - orbitState.current.prevX;
        const dy = e.clientY - orbitState.current.prevY;
        orbitState.current.targetRotY += dx * 0.008;
        orbitState.current.targetRotX += dy * 0.008;
        orbitState.current.targetRotX = Math.max(
          -Math.PI / 2.2,
          Math.min(Math.PI / 2.2, orbitState.current.targetRotX)
        );
        orbitState.current.prevX = e.clientX;
        orbitState.current.prevY = e.clientY;
      } else {
        // Raycast for hover inspection
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(interactiveMeshesRef.current);
        if (intersects.length > 0) {
          dom.style.cursor = "pointer";
          const hit = intersects[0];
          const nodeData = (hit.object as any).userData?.nodeData as GraphNodeData | undefined;
          if (nodeData) {
            hoverRing.position.copy(hit.object.position);
            hoverRing.lookAt(camera.position);
            (hoverRing.material as THREE.MeshBasicMaterial).opacity = 0.85;
            setMouseCoords({
              x: (nodeData.coordinates[0] > 0 ? "+" : "") + nodeData.coordinates[0].toFixed(2),
              y: (nodeData.coordinates[1] > 0 ? "+" : "") + nodeData.coordinates[1].toFixed(2),
              z: (nodeData.coordinates[2] > 0 ? "+" : "") + nodeData.coordinates[2].toFixed(2),
            });
          }
        } else {
          dom.style.cursor = "grab";
          (hoverRing.material as THREE.MeshBasicMaterial).opacity = 0;
        }
      }
    };

    const onPointerUp = (e: PointerEvent) => {
      orbitState.current.isDragging = false;
      try {
        dom.releasePointerCapture(e.pointerId);
      } catch {
        // Ignore if pointer capture already lost
      }
    };

    const onClick = (e: MouseEvent) => {
      const rect = dom.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(interactiveMeshesRef.current);
      if (intersects.length > 0) {
        const hit = intersects[0];
        const nodeData = (hit.object as any).userData?.nodeData as GraphNodeData | undefined;
        if (nodeData) {
          setSelectedNode(nodeData);
        }
      }
    };

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      orbitState.current.targetZoom += e.deltaY * 0.006;
      orbitState.current.targetZoom = Math.max(6, Math.min(18, orbitState.current.targetZoom));
      setZoomLevel(
        Number(((18 - orbitState.current.targetZoom) / (18 - 6) * 1.5 + 0.5).toFixed(1))
      );
    };

    dom.addEventListener("pointerdown", onPointerDown);
    dom.addEventListener("pointermove", onPointerMove);
    dom.addEventListener("pointerup", onPointerUp);
    dom.addEventListener("pointercancel", onPointerUp);
    dom.addEventListener("click", onClick);
    dom.addEventListener("wheel", onWheel, { passive: false });

    // RESIZE LISTENER
    const handleResize = () => {
      if (!container || !renderer || !camera) return;
      const w = container.clientWidth || 800;
      const h = container.clientHeight || 560;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    // ─────────────────────────────────────────────────────────────
    // ANIMATION RENDER LOOP
    // ─────────────────────────────────────────────────────────────
    let clock = new THREE.Clock();

    const animate = () => {
      animationFrameIdRef.current = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Smooth damping interpolation for orbit
      const ease = 0.08;
      orbitState.current.rotX += (orbitState.current.targetRotX - orbitState.current.rotX) * ease;
      orbitState.current.rotY += (orbitState.current.targetRotY - orbitState.current.rotY) * ease;
      orbitState.current.zoom += (orbitState.current.targetZoom - orbitState.current.zoom) * ease;

      // Auto-rotation if enabled & not dragging
      if (isAutoRotate && !orbitState.current.isDragging && !shouldReduceMotion) {
        orbitState.current.targetRotY += 0.0025;
      }

      if (graphGroupRef.current) {
        graphGroupRef.current.rotation.x = orbitState.current.rotX;
        graphGroupRef.current.rotation.y = orbitState.current.rotY;
      }

      camera.position.z = orbitState.current.zoom;

      // Animate pulsing particles along edges
      if (pulseParticlesRef.current) {
        const positions = pulseParticlesRef.current.geometry.attributes.position;
        const count = positions.count;
        for (let i = 0; i < count; i++) {
          let y = positions.getY(i);
          y -= 0.04;
          if (y < -3.8) y = 3.8;
          positions.setY(i, y);
        }
        positions.needsUpdate = true;
      }

      // Animate Pareto Surface wave ripple & beacon
      if (paretoMeshRef.current) {
        const geo = paretoMeshRef.current.geometry as THREE.PlaneGeometry;
        const posAttr = geo.attributes.position;
        const waveTime = elapsedTime * 1.5;
        for (let i = 0; i < posAttr.count; i++) {
          const u = posAttr.getX(i);
          const v = posAttr.getY(i);
          const z =
            Math.sin(u * 0.7 + waveTime) * 0.45 * Math.cos(v * 0.7 + waveTime * 0.8) +
            Math.sin(Math.sqrt(u * u + v * v) * 1.2 - waveTime) * 0.25;
          posAttr.setZ(i, z);
        }
        posAttr.needsUpdate = true;
        geo.computeVertexNormals();
      }

      if (paretoBeaconRef.current) {
        const pulse = 1 + Math.sin(elapsedTime * 4) * 0.15;
        paretoBeaconRef.current.scale.set(pulse, pulse, pulse);
      }

      renderer.render(scene, camera);
    };

    animate();

    // CLEANUP
    return () => {
      if (animationFrameIdRef.current) {
        cancelAnimationFrame(animationFrameIdRef.current);
      }
      window.removeEventListener("resize", handleResize);
      dom.removeEventListener("pointerdown", onPointerDown);
      dom.removeEventListener("pointermove", onPointerMove);
      dom.removeEventListener("pointerup", onPointerUp);
      dom.removeEventListener("pointercancel", onPointerUp);
      dom.removeEventListener("click", onClick);
      dom.removeEventListener("wheel", onWheel);

      renderer.dispose();
      if (dom.parentElement) {
        dom.parentElement.removeChild(dom);
      }
    };
  }, []);

  // ─────────────────────────────────────────────────────────────
  // SCENE BUILDER FOR EACH 3D GRAPH
  // ─────────────────────────────────────────────────────────────
  const rebuildGraphScene = () => {
    const group = graphGroupRef.current;
    if (!group) return;

    // Clear old children safely
    while (group.children.length > 0) {
      const child = group.children[0];
      group.remove(child);
      if ((child as any).geometry) (child as any).geometry.dispose();
      if ((child as any).material) {
        if (Array.isArray((child as any).material)) {
          (child as any).material.forEach((m: any) => m.dispose());
        } else {
          (child as any).material.dispose();
        }
      }
    }

    interactiveMeshesRef.current = [];
    paretoMeshRef.current = null;
    paretoBeaconRef.current = null;
    pulseParticlesRef.current = null;

    if (activeMode === "memory") {
      buildMemoryClusterGraph(group);
    } else if (activeMode === "dag") {
      buildTaskDAGGraph(group);
    } else if (activeMode === "pareto") {
      buildParetoSurfaceGraph(group);
    }
  };

  // ─────────────────────────────────────────────────────────────
  // GRAPH 01: 3D LATENT MEMORY & VECTOR CLUSTERS
  // ─────────────────────────────────────────────────────────────
  const buildMemoryClusterGraph = (group: THREE.Group) => {
    // 3D Bounding Spatial Box
    const boxGeo = new THREE.BoxGeometry(9.6, 7.2, 5.6);
    const boxWire = new THREE.WireframeGeometry(boxGeo);
    const boxMat = new THREE.LineBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.06,
    });
    const boxMesh = new THREE.LineSegments(boxWire, boxMat);
    group.add(boxMesh);

    // Coordinate grid plane at bottom
    const gridHelper = new THREE.GridHelper(9.6, 12, 0xff4a16, 0x1f2429);
    gridHelper.position.y = -3.6;
    group.add(gridHelper);

    // Create 3D Nodes
    const sphereGeo = new THREE.SphereGeometry(0.24, 24, 24);
    const glowGeo = new THREE.SphereGeometry(0.38, 16, 16);

    MEMORY_NODES.forEach((node) => {
      const nodeMat = new THREE.MeshStandardMaterial({
        color: node.color,
        roughness: 0.2,
        metalness: 0.8,
        emissive: node.color,
        emissiveIntensity: 0.5,
      });
      const nodeMesh = new THREE.Mesh(sphereGeo, nodeMat);
      nodeMesh.position.set(...node.coordinates);
      (nodeMesh as any).userData = { nodeData: node };

      // Halo atmosphere
      const glowMat = new THREE.MeshBasicMaterial({
        color: node.color,
        transparent: true,
        opacity: 0.2,
        wireframe: true,
      });
      const glowMesh = new THREE.Mesh(glowGeo, glowMat);
      nodeMesh.add(glowMesh);

      group.add(nodeMesh);
      interactiveMeshesRef.current.push(nodeMesh);
    });

    // Connecting Fibers (Edges within clusters and cross-cluster bridge)
    const lineMat = new THREE.LineBasicMaterial({
      color: 0x4a5568,
      transparent: true,
      opacity: 0.35,
    });
    const bridgeMat = new THREE.LineDashedMaterial({
      color: 0xff4a16,
      transparent: true,
      opacity: 0.75,
      dashSize: 0.25,
      gapSize: 0.15,
    });

    const edgePoints: number[] = [];

    // Connect nodes based on distance threshold
    for (let i = 0; i < MEMORY_NODES.length; i++) {
      for (let j = i + 1; j < MEMORY_NODES.length; j++) {
        const n1 = MEMORY_NODES[i];
        const n2 = MEMORY_NODES[j];
        const dist = Math.hypot(
          n1.coordinates[0] - n2.coordinates[0],
          n1.coordinates[1] - n2.coordinates[1],
          n1.coordinates[2] - n2.coordinates[2]
        );

        if (n1.cluster === n2.cluster || dist < 3.8) {
          const points = [
            new THREE.Vector3(...n1.coordinates),
            new THREE.Vector3(...n2.coordinates),
          ];
          const edgeGeo = new THREE.BufferGeometry().setFromPoints(points);

          let line: THREE.Line;
          if (n1.cluster !== n2.cluster) {
            line = new THREE.Line(edgeGeo, bridgeMat);
            line.computeLineDistances();
          } else {
            line = new THREE.Line(edgeGeo, lineMat);
          }
          group.add(line);

          edgePoints.push(
            (n1.coordinates[0] + n2.coordinates[0]) / 2,
            (n1.coordinates[1] + n2.coordinates[1]) / 2,
            (n1.coordinates[2] + n2.coordinates[2]) / 2
          );
        }
      }
    }

    // Dynamic Photon Particle Cloud along edges
    if (edgePoints.length > 0) {
      const particleGeo = new THREE.BufferGeometry();
      particleGeo.setAttribute("position", new THREE.Float32BufferAttribute(edgePoints, 3));
      const particleMat = new THREE.PointsMaterial({
        color: 0xffaa00,
        size: 0.12,
        transparent: true,
        opacity: 0.9,
      });
      const particles = new THREE.Points(particleGeo, particleMat);
      group.add(particles);
      pulseParticlesRef.current = particles;
    }
  };

  // ─────────────────────────────────────────────────────────────
  // GRAPH 02: 3D AUTONOMOUS TASK DAG & SWARM EXECUTION
  // ─────────────────────────────────────────────────────────────
  const buildTaskDAGGraph = (group: THREE.Group) => {
    // Spatial Axis Guidelines (Z: Depth, Y: Execution Stage, X: Parallel Lanes)
    const axisY = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 4.2, 0),
        new THREE.Vector3(0, -4.2, 0),
      ]),
      new THREE.LineDashedMaterial({ color: 0xff4a16, opacity: 0.4, transparent: true, dashSize: 0.2, gapSize: 0.1 })
    );
    axisY.computeLineDistances();
    group.add(axisY);

    // Build Nodes
    const rootGeo = new THREE.OctahedronGeometry(0.38, 0);
    const workerGeo = new THREE.BoxGeometry(0.42, 0.42, 0.42);
    const coreGeo = new THREE.DodecahedronGeometry(0.46, 0);

    DAG_NODES.forEach((node) => {
      let geo: THREE.BufferGeometry = workerGeo;
      if (node.id === "dag-01") geo = coreGeo; // Master Orchestrator (Gemini 3.8 Flash)
      if (node.id === "dag-00" || node.id === "dag-04") geo = rootGeo;

      const mat = new THREE.MeshStandardMaterial({
        color: node.color,
        metalness: 0.85,
        roughness: 0.2,
        emissive: node.color,
        emissiveIntensity: 0.55,
      });

      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(...node.coordinates);
      (mesh as any).userData = { nodeData: node };

      // Wireframe outer cage
      const wireMat = new THREE.MeshBasicMaterial({
        color: 0xffffff,
        wireframe: true,
        transparent: true,
        opacity: 0.25,
      });
      const wireMesh = new THREE.Mesh(geo, wireMat);
      wireMesh.scale.set(1.28, 1.28, 1.28);
      mesh.add(wireMesh);

      group.add(mesh);
      interactiveMeshesRef.current.push(mesh);
    });

    // Directed Bezier Curves connecting stages
    const connectDAG = (fromId: string, toId: string, color: number) => {
      const fromNode = DAG_NODES.find((n) => n.id === fromId);
      const toNode = DAG_NODES.find((n) => n.id === toId);
      if (!fromNode || !toNode) return;

      const vFrom = new THREE.Vector3(...fromNode.coordinates);
      const vTo = new THREE.Vector3(...toNode.coordinates);

      const vMid = new THREE.Vector3(
        (vFrom.x + vTo.x) / 2,
        (vFrom.y + vTo.y) / 2,
        (vFrom.z + vTo.z) / 2 + 0.6
      );

      const curve = new THREE.QuadraticBezierCurve3(vFrom, vMid, vTo);
      const curvePoints = curve.getPoints(24);
      const curveGeo = new THREE.BufferGeometry().setFromPoints(curvePoints);
      const curveMat = new THREE.LineBasicMaterial({
        color,
        transparent: true,
        opacity: 0.6,
      });
      const line = new THREE.Line(curveGeo, curveMat);
      group.add(line);
    };

    // Orchestration Flow Edges
    connectDAG("dag-00", "dag-01", 0xff4a16); // Ingress -> Gemini 3.8 Flash
    connectDAG("dag-01", "dag-02a", 0xffaa00); // Planner -> AST
    connectDAG("dag-01", "dag-02b", 0xa855f7); // Planner -> Vector
    connectDAG("dag-01", "dag-02c", 0x06b6d4); // Planner -> Web
    connectDAG("dag-01", "dag-02d", 0x10b981); // Planner -> Subagents

    connectDAG("dag-02a", "dag-03a", 0xe9d0ad); // AST -> Socratic
    connectDAG("dag-02b", "dag-03a", 0xe9d0ad); // Vector -> Socratic
    connectDAG("dag-02c", "dag-03b", 0x10b981); // Web -> Sandbox
    connectDAG("dag-02d", "dag-03b", 0x10b981); // Subagents -> Sandbox

    connectDAG("dag-03a", "dag-04", 0xff4a16); // Socratic -> Assembler
    connectDAG("dag-03b", "dag-04", 0xff4a16); // Sandbox -> Assembler
  };

  // ─────────────────────────────────────────────────────────────
  // GRAPH 03: 3D PARETO LATENCY-QUALITY EFFICIENCY MANIFOLD
  // ─────────────────────────────────────────────────────────────
  const buildParetoSurfaceGraph = (group: THREE.Group) => {
    const size = 7.2;
    const segments = 32;
    const planeGeo = new THREE.PlaneGeometry(size, size, segments, segments);

    const posAttr = planeGeo.attributes.position;
    for (let i = 0; i < posAttr.count; i++) {
      const u = posAttr.getX(i);
      const v = posAttr.getY(i);
      const z = Math.sin(u * 0.7) * 0.45 * Math.cos(v * 0.7);
      posAttr.setZ(i, z);
    }
    planeGeo.computeVertexNormals();

    const planeMat = new THREE.MeshStandardMaterial({
      color: 0x11161d,
      roughness: 0.35,
      metalness: 0.8,
      wireframe: true,
      wireframeLinewidth: 1.5,
    });

    const mesh = new THREE.Mesh(planeGeo, planeMat);
    mesh.rotation.x = -Math.PI / 2.4;
    group.add(mesh);
    paretoMeshRef.current = mesh;

    // Outer boundary grid
    const grid = new THREE.GridHelper(8.0, 10, 0xff4a16, 0x242a30);
    grid.position.y = -2.2;
    group.add(grid);

    // Glowing Operating Beacon for APEX (0.003ms Fast Path crest)
    const beaconGroup = new THREE.Group();
    beaconGroup.position.set(0.8, 1.4, 0.4);

    const beaconCore = new THREE.Mesh(
      new THREE.SphereGeometry(0.28, 24, 24),
      new THREE.MeshStandardMaterial({
        color: 0xff4a16,
        emissive: 0xff4a16,
        emissiveIntensity: 0.9,
      })
    );
    beaconGroup.add(beaconCore);

    const beaconRing = new THREE.Mesh(
      new THREE.TorusGeometry(0.5, 0.02, 16, 32),
      new THREE.MeshBasicMaterial({ color: 0xffaa00 })
    );
    beaconRing.rotation.x = Math.PI / 2;
    beaconGroup.add(beaconRing);

    group.add(beaconGroup);
    paretoBeaconRef.current = beaconGroup;

    (beaconCore as any).userData = {
      nodeData: {
        id: "apex-operating-point",
        name: "APEX // Sovereign Operating Point",
        category: "Pareto Frontier",
        layer: "All 24 Layers Unified",
        cluster: "Efficiency Manifold",
        latency: "0.003 ms Reflex Skip",
        status: "OPTIMAL",
        description: "Optimal trade-off locus: Sub-10µs routing, 12.4x AST token compression, and 100% verification pass rate.",
        coordinates: [0.8, 1.4, 0.4],
        color: 0xff4a16,
      },
    };
    interactiveMeshesRef.current.push(beaconCore);
    setSelectedNode((beaconCore as any).userData.nodeData);
  };

  const handleResetCamera = () => {
    orbitState.current.targetRotX = 0.25;
    orbitState.current.targetRotY = -0.35;
    orbitState.current.targetZoom = 11;
    setZoomLevel(1);
  };

  const handleZoom = (delta: number) => {
    orbitState.current.targetZoom = Math.max(6, Math.min(18, orbitState.current.targetZoom + delta));
    setZoomLevel(
      Number(((18 - orbitState.current.targetZoom) / (18 - 6) * 1.5 + 0.5).toFixed(1))
    );
  };

  return (
    <section
      id="topology"
      ref={containerRef}
      className="relative w-full bg-[#050607] text-[#F5F3EF] py-16 sm:py-20 lg:py-28 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="3D Spatial Topology and Knowledge Graphs"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Section Header */}
        <div className="max-w-[900px] mb-8 lg:mb-12">
          {/* Eyebrow */}
          <div className="flex items-center gap-3 mb-4">
            <motion.span
              initial={shouldReduceMotion ? { width: 24 } : { width: 0 }}
              whileInView={{ width: 24 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, ease: MOTION_EASE.enter }}
              className="h-px bg-[#FF4A16] block"
              aria-hidden="true"
            />
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1, x: 0 } : { opacity: 0, x: -8 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1, ease: MOTION_EASE.enter }}
              className="font-code text-[10px] sm:text-[11px] tracking-[0.28em] text-[#737575] uppercase font-medium flex items-center gap-2"
            >
              <span>3D SPATIAL TOPOLOGY</span>
              <span className="text-[#FF4A16]/70">·</span>
              <span className="text-[#FF4A16]">WEBGL HARDWARE PIPELINE</span>
            </motion.div>
          </div>

          {/* Headline */}
          <h2 className="font-editorial text-4xl sm:text-6xl lg:text-7xl leading-[1.04] tracking-[-0.02em] text-[#F5F3EF] mb-5 flex flex-col">
            <span className="overflow-mask block relative py-0.5">
              <motion.span
                initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: "110%" }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.75, ease: MOTION_EASE.enter }}
                className="block font-normal"
              >
                Intelligence has geometry.
              </motion.span>
            </span>
            <span className="overflow-mask block relative py-0.5">
              <motion.span
                initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: "110%" }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.85, delay: 0.1, ease: MOTION_EASE.enter }}
                className="block font-editorial italic font-normal text-[#E9D0AD]"
              >
                Explore it in 3D.
              </motion.span>
            </span>
          </h2>

          <motion.p
            initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2, ease: MOTION_EASE.enter }}
            className="text-[#B2B0AD] text-base sm:text-lg font-normal leading-relaxed max-w-[700px]"
          >
            Direct your cursor to rotate and explore APEX&apos;s latent memory manifolds, autonomous multi-agent task DAGs, and Pareto latency frontiers in interactive 3D Euclidean space.
          </motion.p>
        </div>

        {/* 3D Graph Switcher Tabs */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-6 pb-4 border-b border-[rgba(255,255,255,0.08)]">
          {/* Switcher Buttons */}
          <div className="flex flex-wrap items-center gap-2" role="tablist" aria-label="3D Graph Selection">
            <button
              role="tab"
              aria-selected={activeMode === "memory"}
              type="button"
              onClick={() => setActiveMode("memory")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-code transition-all cursor-pointer focus-visible:outline-[#FF4A16] ${
                activeMode === "memory"
                  ? "bg-[#FF4A16] text-white shadow-[0_0_16px_rgba(255,74,22,0.4)] font-semibold"
                  : "bg-[#111315] text-[#8C9295] hover:text-[#F5F3EF] hover:bg-[#16191c]"
              }`}
            >
              <Database size={13} />
              <span>01 // LATENT MEMORY CLUSTERS</span>
            </button>

            <button
              role="tab"
              aria-selected={activeMode === "dag"}
              type="button"
              onClick={() => setActiveMode("dag")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-code transition-all cursor-pointer focus-visible:outline-[#FF4A16] ${
                activeMode === "dag"
                  ? "bg-[#FF4A16] text-white shadow-[0_0_16px_rgba(255,74,22,0.4)] font-semibold"
                  : "bg-[#111315] text-[#8C9295] hover:text-[#F5F3EF] hover:bg-[#16191c]"
              }`}
            >
              <Workflow size={13} />
              <span>02 // TASK EXECUTION DAG</span>
            </button>

            <button
              role="tab"
              aria-selected={activeMode === "pareto"}
              type="button"
              onClick={() => setActiveMode("pareto")}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-code transition-all cursor-pointer focus-visible:outline-[#FF4A16] ${
                activeMode === "pareto"
                  ? "bg-[#FF4A16] text-white shadow-[0_0_16px_rgba(255,74,22,0.4)] font-semibold"
                  : "bg-[#111315] text-[#8C9295] hover:text-[#F5F3EF] hover:bg-[#16191c]"
              }`}
            >
              <Activity size={13} />
              <span>03 // PARETO METRIC MANIFOLD</span>
            </button>
          </div>

          {/* Viewport Control Badges */}
          <div className="flex items-center gap-2 font-code text-[11px] text-[#8C9295]">
            <button
              type="button"
              onClick={() => setIsAutoRotate(!isAutoRotate)}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded border text-[11px] transition-all cursor-pointer ${
                isAutoRotate
                  ? "border-[#FF4A16]/50 text-[#FF4A16] bg-[#FF4A16]/10"
                  : "border-[rgba(255,255,255,0.1)] text-[#737575] hover:text-[#F5F3EF]"
              }`}
              title="Toggle Auto-Orbit"
            >
              <RotateCw size={12} className={isAutoRotate ? "animate-spin" : ""} style={{ animationDuration: "6s" }} />
              <span className="hidden sm:inline">ORBIT</span>
            </button>

            <button
              type="button"
              onClick={() => handleZoom(-1.5)}
              className="p-1.5 rounded border border-[rgba(255,255,255,0.1)] hover:text-[#F5F3EF] hover:border-[rgba(255,255,255,0.25)] transition-all cursor-pointer"
              title="Zoom In"
            >
              <ZoomIn size={12} />
            </button>

            <button
              type="button"
              onClick={() => handleZoom(1.5)}
              className="p-1.5 rounded border border-[rgba(255,255,255,0.1)] hover:text-[#F5F3EF] hover:border-[rgba(255,255,255,0.25)] transition-all cursor-pointer"
              title="Zoom Out"
            >
              <ZoomOut size={12} />
            </button>

            <button
              type="button"
              onClick={handleResetCamera}
              className="p-1.5 rounded border border-[rgba(255,255,255,0.1)] hover:text-[#F5F3EF] hover:border-[rgba(255,255,255,0.25)] transition-all cursor-pointer"
              title="Reset View"
            >
              <Maximize2 size={12} />
            </button>
          </div>
        </div>

        {/* Main 3D Viewport & Inspection Stage */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          {/* Left/Center: 3D Interactive WebGL Canvas Container */}
          <div className="lg:col-span-8 bg-[#08090A] border border-[rgba(255,255,255,0.1)] rounded-2xl relative overflow-hidden h-[500px] sm:h-[580px] lg:h-[620px] flex flex-col justify-between shadow-[0_20px_50px_rgba(0,0,0,0.6)]">
            {/* Top Bar HUD */}
            <div className="relative z-10 p-4 sm:p-5 flex items-center justify-between border-b border-[rgba(255,255,255,0.06)] bg-[#08090A]/80 backdrop-blur-md font-code text-xs">
              <div className="flex items-center gap-3">
                <span className="w-2 h-2 rounded-full bg-[#FF4A16] shadow-[0_0_8px_#FF4A16] animate-pulse" />
                <span className="text-[#F5F3EF] font-semibold tracking-wider uppercase text-[11px]">
                  {activeMode === "memory" && "TOPOLOGY // LATENT SEMANTIC CLUSTERS (D=1536)"}
                  {activeMode === "dag" && "TOPOLOGY // DIRECTED ACYCLIC GRAPH (5 TIERS)"}
                  {activeMode === "pareto" && "TOPOLOGY // 3D HYPERBOLIC EFFICIENCY FRONTIER"}
                </span>
              </div>

              {/* Coordinates tracker */}
              <div className="hidden sm:flex items-center gap-3 text-[10px] text-[#737575]">
                <span>X: <strong className="text-[#F5F3EF]">{mouseCoords.x}</strong></span>
                <span>Y: <strong className="text-[#F5F3EF]">{mouseCoords.y}</strong></span>
                <span>Z: <strong className="text-[#F5F3EF]">{mouseCoords.z}</strong></span>
                <span className="text-[#FF4A16] pl-2 border-l border-[rgba(255,255,255,0.1)]">
                  ZOOM: {zoomLevel}x
                </span>
              </div>
            </div>

            {/* Three.js Canvas Mount */}
            <div
              ref={canvasWrapperRef}
              className="relative w-full flex-1 touch-none cursor-grab active:cursor-grabbing overflow-hidden"
              role="img"
              aria-label="3D Interactive Graph Canvas. Drag with mouse to orbit."
            >
              {!webglSupported && (
                <div className="absolute inset-0 flex items-center justify-center p-6 text-center bg-[#08090A]">
                  <p className="font-code text-xs text-[#737575]">
                    WebGL is disabled or unsupported on this display device.
                  </p>
                </div>
              )}

              {/* Drag instruction overlay badge */}
              <div className="absolute bottom-4 left-4 z-10 pointer-events-none flex items-center gap-2 bg-[#050607]/80 backdrop-blur-md border border-[rgba(255,255,255,0.08)] px-3 py-1.5 rounded-full text-[10px] font-code text-[#B2B0AD]">
                <Share2 size={11} className="text-[#FF4A16]" />
                <span>DRAG TO ORBIT · SCROLL TO ZOOM · CLICK NODE TO INSPECT</span>
              </div>
            </div>

            {/* Bottom HUD Bar */}
            <div className="relative z-10 px-5 py-3 border-t border-[rgba(255,255,255,0.06)] bg-[#08090A]/90 backdrop-blur-md flex flex-wrap items-center justify-between text-[11px] font-code text-[#737575]">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
                  <span>RENDERER: THREE.JS WEBGL</span>
                </span>
                <span className="hidden md:inline">
                  SHADING: METALLIC PBR
                </span>
              </div>
              <span className="text-[#FF4A16] uppercase font-medium">
                {activeMode === "memory" && "12 ACTIVE SYMBOL/VECTOR NODES"}
                {activeMode === "dag" && "8 PIPELINE STAGES · 11 DIRECTED ARCS"}
                {activeMode === "pareto" && "CONTINUOUS HYPERBOLIC PARAMETRIC MESH"}
              </span>
            </div>
          </div>

          {/* Right: Glassmorphic Node Telemetry & Attribute Inspector */}
          <div className="lg:col-span-4 flex flex-col justify-between bg-[#08090A] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 sm:p-8 relative overflow-hidden min-h-[500px]">
            <div className="absolute inset-0 architectural-grid opacity-20 pointer-events-none" />

            <div>
              {/* Header */}
              <div className="flex items-center justify-between pb-3.5 border-b border-[rgba(255,255,255,0.08)] mb-6">
                <span className="font-code text-[11px] tracking-wider text-[#FF4A16] uppercase font-semibold flex items-center gap-2">
                  <Sparkles size={12} />
                  <span>NODE INSPECTION ENGINE</span>
                </span>
                <span className="font-code text-[10px] text-[#737575] uppercase">
                  ACTIVE SELECTION
                </span>
              </div>

              {/* Selected Node Content */}
              {selectedNode ? (
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className="w-2.5 h-2.5 rounded-full shrink-0"
                      style={{
                        backgroundColor: "#" + selectedNode.color.toString(16).padStart(6, "0"),
                        boxShadow: `0 0 10px #${selectedNode.color.toString(16).padStart(6, "0")}`,
                      }}
                    />
                    <span className="font-code text-xs text-[#8C9295] uppercase tracking-wider">
                      {selectedNode.category}
                    </span>
                    <span className="ml-auto font-code text-[10px] px-2 py-0.5 rounded bg-[rgba(255,255,255,0.05)] text-[#E9D0AD] border border-[rgba(255,255,255,0.08)]">
                      {selectedNode.status}
                    </span>
                  </div>

                  <h3 className="font-code text-xl sm:text-2xl font-bold text-[#F5F3EF] mb-2 tracking-tight">
                    {selectedNode.name}
                  </h3>

                  <p className="text-xs sm:text-sm text-[#B2B0AD] leading-relaxed mb-6 font-sans">
                    {selectedNode.description}
                  </p>

                  {/* Node Attribute Matrix */}
                  <div className="space-y-2.5 mb-6">
                    <div className="p-3 rounded-xl bg-[#111315] border border-[rgba(255,255,255,0.06)] flex items-center justify-between text-xs font-code">
                      <span className="text-[#737575]">OPERATIONAL LAYER</span>
                      <span className="text-[#F5F3EF] font-semibold">{selectedNode.layer}</span>
                    </div>

                    <div className="p-3 rounded-xl bg-[#111315] border border-[rgba(255,255,255,0.06)] flex items-center justify-between text-xs font-code">
                      <span className="text-[#737575]">CLUSTER ASSIGNMENT</span>
                      <span className="text-[#E9D0AD] font-semibold">{selectedNode.cluster}</span>
                    </div>

                    <div className="p-3 rounded-xl bg-[#111315] border border-[rgba(255,255,255,0.06)] flex items-center justify-between text-xs font-code">
                      <span className="text-[#737575]">MEASURED LATENCY</span>
                      <span className="text-[#FF4A16] font-bold">{selectedNode.latency}</span>
                    </div>

                    <div className="p-3 rounded-xl bg-[#111315] border border-[rgba(255,255,255,0.06)] flex items-center justify-between text-xs font-code">
                      <span className="text-[#737575]">COORDINATE VECTOR</span>
                      <span className="text-[#B2B0AD]">
                        [{selectedNode.coordinates.map((c) => c.toFixed(1)).join(", ")}]
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center text-[#737575] font-code text-xs">
                  Hover or click any 3D node on the canvas to inspect its telemetry vector.
                </div>
              )}
            </div>

            {/* Quick Filter Node List for Quick Switching */}
            <div className="pt-4 border-t border-[rgba(255,255,255,0.08)]">
              <span className="block font-code text-[10px] text-[#737575] uppercase tracking-wider mb-2.5">
                QUICK JUMP TO KEY TOPOLOGY NODES:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {(activeMode === "memory" ? MEMORY_NODES : DAG_NODES).slice(0, 4).map((node) => (
                  <button
                    key={node.id}
                    type="button"
                    onClick={() => setSelectedNode(node)}
                    className={`px-2.5 py-1 rounded text-[10px] font-code transition-all cursor-pointer ${
                      selectedNode?.id === node.id
                        ? "bg-[#FF4A16] text-white"
                        : "bg-[#111315] text-[#8C9295] hover:text-[#F5F3EF]"
                    }`}
                  >
                    {node.name.split("::")[0] || node.name.split("//")[0]}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
