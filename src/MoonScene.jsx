import React, { Suspense, useLayoutEffect, useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera, useGLTF } from "@react-three/drei";
import * as THREE from "three";

const MOOD_LOOKS = {
  angry: { aura: "rgba(255, 170, 155, 0.24)", light: "#ffb9aa", subtitle: "firm but calm" },
  sad: { aura: "rgba(190, 207, 255, 0.22)", light: "#d6e1ff", subtitle: "soft and close" },
  anxious: { aura: "rgba(178, 233, 255, 0.24)", light: "#d6f4ff", subtitle: "gentle and attentive" },
  overwhelmed: { aura: "rgba(212, 201, 255, 0.22)", light: "#e3dbff", subtitle: "holding steady with you" },
  tired: { aura: "rgba(255, 229, 198, 0.2)", light: "#f6ddbf", subtitle: "sleepy and warm" },
  hopeful: { aura: "rgba(255, 228, 166, 0.24)", light: "#ffe6b7", subtitle: "bright and reassuring" },
  neutral: { aura: "rgba(255, 236, 204, 0.2)", light: "#f8e4c8", subtitle: "quietly with you" },
};

function truncateCaption(text) {
  const clean = (text || "").trim();
  if (!clean) return "Luna is here with you.";
  return clean.length > 110 ? `${clean.slice(0, 110).trimEnd()}...` : clean;
}

function ModelRig({ isSpeaking }) {
  const rootRef = useRef(null);
  const gltf = useGLTF("/girl_face_002.glb");
  const cloned = useMemo(() => gltf.scene.clone(true), [gltf.scene]);
  const jawBonesRef = useRef([]);
  const headBonesRef = useRef([]);
  const mouthMeshesRef = useRef([]);
  const speechOpenRef = useRef(0);

  useLayoutEffect(() => {
    const box = new THREE.Box3().setFromObject(cloned);
    const size = new THREE.Vector3();
    const center = new THREE.Vector3();
    box.getSize(size);
    box.getCenter(center);

    const longest = Math.max(size.x, size.y, size.z) || 1;
    const scale = 3.45 / longest;

    cloned.scale.setScalar(scale);
    cloned.position.set(-center.x * scale, -center.y * scale + 0.08, -center.z * scale);

    jawBonesRef.current = [];
    headBonesRef.current = [];
    mouthMeshesRef.current = [];

    cloned.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
        const meshName = child.name.toLowerCase();
        if (meshName.includes("mouth") || meshName.includes("lip")) {
          mouthMeshesRef.current.push({
            mesh: child,
            scaleY: child.scale.y,
            positionY: child.position.y,
            morphInfluences: child.morphTargetInfluences ? [...child.morphTargetInfluences] : null,
          });
        }
        if (child.material) {
          const materials = Array.isArray(child.material) ? child.material : [child.material];
          materials.forEach((material) => {
            if (material.map) {
              material.map.colorSpace = THREE.SRGBColorSpace;
              material.map.anisotropy = 8;
            }
            material.side = THREE.FrontSide;
            material.roughness = material.roughness ?? 0.72;
            material.metalness = material.metalness ?? 0.02;
            if (material.emissive) {
              material.emissive.set("#000000");
              material.emissiveIntensity = 0;
            }
            material.needsUpdate = true;
          });
        }
      }

      if (child.isBone) {
        const name = child.name.toLowerCase();
        if (name.includes("jaw") || name.includes("mouth") || name.includes("lip")) {
          jawBonesRef.current.push({
            bone: child,
            rotationX: child.rotation.x,
            rotationY: child.rotation.y,
            positionY: child.position.y,
          });
        }

        if (name.includes("head") || name.includes("neck")) {
          headBonesRef.current.push({
            bone: child,
            rotationX: child.rotation.x,
            rotationY: child.rotation.y,
          });
        }
      }
    });
  }, [cloned]);

  useFrame(({ clock }, delta) => {
    const t = clock.getElapsedTime();
    const group = rootRef.current;
    if (!group) return;

    group.position.y = Math.sin(t * 1.1) * 0.025;
    group.rotation.y = 0;
    group.rotation.x = -0.08;

    const rawSpeak = isSpeaking ? 0.22 + Math.max(0, Math.sin(t * 6.2)) * 0.78 : 0;
    speechOpenRef.current = THREE.MathUtils.damp(speechOpenRef.current, rawSpeak, isSpeaking ? 10 : 14, delta);
    const speakAmount = speechOpenRef.current;
    const headNod = isSpeaking ? Math.sin(t * 3.1) * 0.008 : 0;

    jawBonesRef.current.forEach(({ bone, rotationX, rotationY, positionY }) => {
      bone.rotation.x = rotationX + speakAmount * 0.28;
      bone.rotation.y = rotationY;
      bone.position.y = positionY - speakAmount * 0.01;
    });

    mouthMeshesRef.current.forEach(({ mesh, scaleY, positionY, morphInfluences }) => {
      mesh.scale.y = scaleY + speakAmount * 0.12;
      mesh.position.y = positionY - speakAmount * 0.01;
      if (morphInfluences) {
        for (let i = 0; i < morphInfluences.length; i += 1) {
          mesh.morphTargetInfluences[i] = i === 0 ? speakAmount * 0.9 : 0;
        }
      }
    });

    headBonesRef.current.forEach(({ bone, rotationX, rotationY }) => {
      bone.rotation.x = rotationX + headNod;
      bone.rotation.y = rotationY;
    });
  });

  return (
    <group ref={rootRef} rotation-y={Math.PI}>
      <primitive object={cloned} />
    </group>
  );
}

function LunaViewport({ mood, isSpeaking }) {
  const look = MOOD_LOOKS[mood] || MOOD_LOOKS.neutral;

  return (
    <Canvas shadows dpr={[1, 1.5]} gl={{ antialias: true, alpha: true }}>
      <color attach="background" args={["#0a1024"]} />
      <fog attach="fog" args={["#0a1024", 7, 18]} />
      <PerspectiveCamera makeDefault position={[0, 0.92, 7.8]} fov={23} />
      <ambientLight intensity={1.6} color="#d6deff" />
      <directionalLight position={[2.5, 3.5, 5.5]} intensity={2.4} color="#fff8f1" castShadow />
      <directionalLight position={[-3.2, 1.8, 3]} intensity={1.05} color={look.light} />
      <pointLight position={[0, 2.2, 2.8]} intensity={1.6} color={look.light} distance={12} />
      <spotLight position={[0, 5, 4.2]} angle={0.44} penumbra={0.9} intensity={1.6} color="#ffffff" />

      <mesh position={[0, -2.5, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <circleGeometry args={[3.4, 64]} />
        <shadowMaterial transparent opacity={0.28} />
      </mesh>

      <Suspense fallback={null}>
        <ModelRig isSpeaking={isSpeaking} />
      </Suspense>

      <OrbitControls enableZoom={false} enablePan={false} enableRotate={false} autoRotate={false} target={[0, 0.8, 0]} />
    </Canvas>
  );
}

useGLTF.preload("/girl_face_002.glb");

export default function MoonScene({ mood = "neutral", isSpeaking = false, activeText = "" }) {
  const look = MOOD_LOOKS[mood] || MOOD_LOOKS.neutral;
  const caption = useMemo(() => truncateCaption(activeText), [activeText]);

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        borderRadius: "24px",
        background: `
          radial-gradient(circle at 18% 16%, rgba(255,255,255,0.12), transparent 22%),
          radial-gradient(circle at 78% 18%, rgba(128,162,255,0.12), transparent 18%),
          linear-gradient(180deg, rgba(13,19,44,0.92), rgba(6,10,28,0.98)),
          linear-gradient(135deg, #27335e 0%, #314879 36%, #24355d 64%, #111833 100%)
        `,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `
            radial-gradient(circle at 50% 24%, ${look.aura}, transparent 28%),
            repeating-linear-gradient(
              180deg,
              rgba(255,255,255,0.04) 0px,
              rgba(255,255,255,0.04) 1px,
              transparent 2px,
              transparent 7px
            )
          `,
          pointerEvents: "none",
        }}
      />

      <div
        style={{
          position: "absolute",
          inset: "18px 18px 106px",
          borderRadius: "28px",
          overflow: "hidden",
          background: "radial-gradient(circle at 50% 18%, rgba(94, 122, 199, 0.26), rgba(10, 13, 34, 0.36) 52%, rgba(6, 10, 28, 0.16) 100%)",
          boxShadow: `
            inset 0 0 0 1px rgba(255,255,255,0.06),
            0 28px 70px rgba(0,0,0,0.34),
            0 0 90px ${isSpeaking ? look.aura.replace("0.24", "0.18").replace("0.22", "0.18").replace("0.2", "0.18") : "rgba(160,190,255,0.08)"}
          `,
        }}
      >
        <LunaViewport mood={mood} isSpeaking={isSpeaking} />

        <div
          style={{
            position: "absolute",
            inset: 0,
            boxShadow: "inset 0 0 0 1px rgba(255,255,255,0.07), inset 0 -70px 120px rgba(9, 12, 30, 0.58)",
            borderRadius: "28px",
            pointerEvents: "none",
          }}
        />
      </div>

      <div
        style={{
          position: "absolute",
          left: "18px",
          right: "18px",
          bottom: "18px",
          padding: "14px 16px",
          borderRadius: "18px",
          background: "linear-gradient(180deg, rgba(8,12,26,0.44), rgba(8,12,26,0.82))",
          border: "1px solid rgba(255,255,255,0.12)",
          color: "#f5f7ff",
          backdropFilter: "blur(10px)",
          boxShadow: "0 18px 50px rgba(0,0,0,0.2)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: "12px",
            alignItems: "center",
            marginBottom: "6px",
            fontSize: "0.74rem",
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            color: look.light,
          }}
        >
          <span>Luna</span>
          <span>{isSpeaking ? "speaking" : "listening"}</span>
        </div>
        <div style={{ fontSize: "0.92rem", lineHeight: 1.45 }}>{caption}</div>
        <div style={{ marginTop: "6px", fontSize: "0.78rem", color: "rgba(242,244,255,0.66)" }}>{look.subtitle}</div>
      </div>
    </div>
  );
}
