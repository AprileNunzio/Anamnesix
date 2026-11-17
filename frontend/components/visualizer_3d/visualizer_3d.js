class Clinical3DVisualizer {
  constructor(canvasId, tooltipId) {
    this.canvas = document.getElementById(canvasId);
    this.tooltip = document.getElementById(tooltipId);
    this.currentMode = "body";
    this.organMeshes = [];
    this.dnaGroup = null;
    this.bodyGroup = null;
    this.cardioGroup = null;
    this.mouse = { x: 0, y: 0 };
    this.isDragging = false;
    this.previousMousePosition = { x: 0, y: 0 };
    this.targetRotation = { x: 0, y: 0 };
    this.anomalies = [];

    if (this.canvas && window.THREE) {
      this.initThree();
    }
  }

  setAnomalies(anomaliesList) {
    this.anomalies = anomaliesList || [];
    this.updateOrganColors();
  }

  initThree() {
    const width = this.canvas.clientWidth || 600;
    const height = this.canvas.clientHeight || 340;

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    this.camera.position.z = 18;

    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true
    });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    this.scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x0284c7, 1.2);
    dirLight1.position.set(5, 10, 7);
    this.scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x38bdf8, 0.8);
    dirLight2.position.set(-5, -5, 5);
    this.scene.add(dirLight2);

    this.raycaster = new THREE.Raycaster();

    this.buildBodyModel();
    this.buildDNAModel();
    this.buildCardioModel();

    this.switchMode("body");
    this.bindEvents();
    this.animate();
  }

  buildBodyModel() {
    this.bodyGroup = new THREE.Group();

    const bodyPoints = [];
    for (let i = 0; i < 450; i++) {
      const u = Math.random();
      const v = Math.random();
      const theta = u * 2.0 * Math.PI;
      const phi = Math.acos(2.0 * v - 1.0);
      const r = 2.4 * Math.cbrt(Math.random());
      const sinPhi = Math.sin(phi);
      const x = r * sinPhi * Math.cos(theta) * 0.45;
      const y = (Math.random() - 0.5) * 8.5;
      const z = r * sinPhi * Math.sin(theta) * 0.25;
      bodyPoints.push(new THREE.Vector3(x, y, z));
    }
    const geom = new THREE.BufferGeometry().setFromPoints(bodyPoints);
    const mat = new THREE.PointsMaterial({
      color: 0x94a3b8,
      size: 0.12,
      transparent: true,
      opacity: 0.55
    });
    const pointsMesh = new THREE.Points(geom, mat);
    this.bodyGroup.add(pointsMesh);

    const organsData = [
      { name: "Tiroide", position: [0, 2.7, 0.4], category: "Tiroide", baseColor: 0x16a34a, radius: 0.32 },
      { name: "Cuore", position: [-0.4, 1.4, 0.5], category: "Metabolico", baseColor: 0x16a34a, radius: 0.42 },
      { name: "Fegato", position: [0.55, 0.5, 0.5], category: "Funzionalita Epatica", baseColor: 0x16a34a, radius: 0.45 },
      { name: "Reni", position: [-0.5, -0.2, -0.2], category: "Funzionalita Renale", baseColor: 0x16a34a, radius: 0.35 },
      { name: "Asse Metabolico / Intestino", position: [0, -0.9, 0.4], category: "Profilo Lipidico", baseColor: 0x16a34a, radius: 0.40 },
      { name: "Apparato Riproduttivo / Gonadi", position: [0, -2.1, 0.3], category: "Fertilita", baseColor: 0x16a34a, radius: 0.38 }
    ];

    organsData.forEach(org => {
      const sGeom = new THREE.SphereGeometry(org.radius, 24, 24);
      const sMat = new THREE.MeshStandardMaterial({
        color: org.baseColor,
        roughness: 0.2,
        metalness: 0.3,
        emissive: org.baseColor,
        emissiveIntensity: 0.35
      });
      const mesh = new THREE.Mesh(sGeom, sMat);
      mesh.position.set(...org.position);
      mesh.userData = {
        name: org.name,
        category: org.category,
        baseColor: org.baseColor
      };
      this.bodyGroup.add(mesh);
      this.organMeshes.push(mesh);
    });

    this.scene.add(this.bodyGroup);
  }

  buildDNAModel() {
    this.dnaGroup = new THREE.Group();
    const count = 38;
    const radius = 1.6;
    const height = 9.0;

    for (let i = 0; i < count; i++) {
      const t = (i / count) * Math.PI * 4.0;
      const y = (i / count) * height - height / 2.0;
      const x1 = Math.cos(t) * radius;
      const z1 = Math.sin(t) * radius;
      const x2 = Math.cos(t + Math.PI) * radius;
      const z2 = Math.sin(t + Math.PI) * radius;

      const pGeom = new THREE.SphereGeometry(0.18, 16, 16);
      const pMat1 = new THREE.MeshStandardMaterial({ color: 0x0284c7, emissive: 0x0284c7, emissiveIntensity: 0.4 });
      const pMat2 = new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x38bdf8, emissiveIntensity: 0.4 });

      const m1 = new THREE.Mesh(pGeom, pMat1);
      m1.position.set(x1, y, z1);
      this.dnaGroup.add(m1);

      const m2 = new THREE.Mesh(pGeom, pMat2);
      m2.position.set(x2, y, z2);
      this.dnaGroup.add(m2);

      const rungPoints = [new THREE.Vector3(x1, y, z1), new THREE.Vector3(x2, y, z2)];
      const rungGeom = new THREE.BufferGeometry().setFromPoints(rungPoints);
      const rungColor = i % 2 === 0 ? 0x10b981 : 0xa855f7;
      const rungMat = new THREE.LineBasicMaterial({ color: rungColor, linewidth: 2 });
      const rungLine = new THREE.Line(rungGeom, rungMat);
      this.dnaGroup.add(rungLine);
    }
    this.dnaGroup.visible = false;
    this.scene.add(this.dnaGroup);
  }

  buildCardioModel() {
    this.cardioGroup = new THREE.Group();
    const torusGeom = new THREE.TorusGeometry(2.8, 0.35, 20, 80);
    const torusMat = new THREE.MeshStandardMaterial({
      color: 0xef4444,
      roughness: 0.3,
      emissive: 0xdc2626,
      emissiveIntensity: 0.5
    });
    this.cardioTorus = new THREE.Mesh(torusGeom, torusMat);
    this.cardioGroup.add(this.cardioTorus);

    const innerSphereGeom = new THREE.SphereGeometry(1.2, 32, 32);
    const innerSphereMat = new THREE.MeshStandardMaterial({
      color: 0x0284c7,
      roughness: 0.2,
      metalness: 0.4,
      emissive: 0x0369a1,
      emissiveIntensity: 0.6
    });
    this.cardioCore = new THREE.Mesh(innerSphereGeom, innerSphereMat);
    this.cardioGroup.add(this.cardioCore);

    this.cardioGroup.visible = false;
    this.scene.add(this.cardioGroup);
  }

  updateOrganColors() {
    if (!this.organMeshes || this.organMeshes.length === 0) {
      return;
    }
    const catAnomalies = {};
    this.anomalies.forEach(a => {
      const cat = a.categoria || "";
      catAnomalies[cat] = (catAnomalies[cat] || 0) + 1;
    });

    this.organMeshes.forEach(mesh => {
      const cat = mesh.userData.category;
      const count = catAnomalies[cat] || 0;
      let newColor = 0x16a34a;
      let emissiveIntensity = 0.3;

      if (count >= 3) {
        newColor = 0xdc2626;
        emissiveIntensity = 0.85;
      } else if (count >= 1) {
        newColor = 0xd97706;
        emissiveIntensity = 0.6;
      }
      mesh.material.color.setHex(newColor);
      mesh.material.emissive.setHex(newColor);
      mesh.material.emissiveIntensity = emissiveIntensity;
      mesh.userData.anomalyCount = count;
    });
  }

  switchMode(mode) {
    this.currentMode = mode;
    if (this.bodyGroup) {
      this.bodyGroup.visible = mode === "body";
    }
    if (this.dnaGroup) {
      this.dnaGroup.visible = mode === "dna";
    }
    if (this.cardioGroup) {
      this.cardioGroup.visible = mode === "cardio";
    }
  }

  bindEvents() {
    this.canvas.addEventListener("mousedown", e => {
      this.isDragging = true;
      this.previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    window.addEventListener("mouseup", () => {
      this.isDragging = false;
    });

    this.canvas.addEventListener("mousemove", e => {
      const rect = this.canvas.getBoundingClientRect();
      this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      if (this.isDragging) {
        const deltaX = e.clientX - this.previousMousePosition.x;
        const deltaY = e.clientY - this.previousMousePosition.y;
        this.targetRotation.y += deltaX * 0.008;
        this.targetRotation.x += deltaY * 0.008;
        this.previousMousePosition = { x: e.clientX, y: e.clientY };
      }

      this.checkRaycast(e.clientX - rect.left, e.clientY - rect.top);
    });

    this.canvas.addEventListener("mouseleave", () => {
      if (this.tooltip) {
        this.tooltip.style.display = "none";
      }
    });

    window.addEventListener("resize", () => {
      const w = this.canvas.clientWidth;
      const h = this.canvas.clientHeight;
      if (w > 0 && h > 0 && this.camera && this.renderer) {
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
      }
    });

    document.querySelectorAll(".btn-3d-mode").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".btn-3d-mode").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.switchMode(btn.getAttribute("data-mode"));
      });
    });
  }

  checkRaycast(mouseX, mouseY) {
    if (this.currentMode !== "body" || !this.tooltip) {
      if (this.tooltip) {
        this.tooltip.style.display = "none";
      }
      return;
    }

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const intersects = this.raycaster.intersectObjects(this.organMeshes);

    if (intersects.length > 0) {
      const hit = intersects[0].object;
      const count = hit.userData.anomalyCount || 0;
      const statusText = count === 0 ? "Stato Fisiologico Regolare" : `${count} parametro/i anomalo/i rilevato/i`;
      const titleEl = document.getElementById("hud-organ-title");
      const statusEl = document.getElementById("hud-organ-status");
      const detailsEl = document.getElementById("hud-organ-details");

      if (titleEl) {
        titleEl.textContent = hit.userData.name;
      }
      if (statusEl) {
        statusEl.textContent = statusText;
        statusEl.style.color = count === 0 ? "#16a34a" : (count >= 3 ? "#ef4444" : "#f59e0b");
      }
      if (detailsEl) {
        detailsEl.textContent = `Categoria: ${hit.userData.category}`;
      }

      this.tooltip.style.left = `${mouseX + 12}px`;
      this.tooltip.style.top = `${mouseY + 12}px`;
      this.tooltip.style.display = "block";
    } else {
      this.tooltip.style.display = "none";
    }
  }

  animate() {
    requestAnimationFrame(() => this.animate());

    const activeGroup = this.currentMode === "body" ? this.bodyGroup : (this.currentMode === "dna" ? this.dnaGroup : this.cardioGroup);

    if (activeGroup) {
      activeGroup.rotation.y += (this.targetRotation.y - activeGroup.rotation.y) * 0.08;
      activeGroup.rotation.x += (this.targetRotation.x - activeGroup.rotation.x) * 0.08;

      if (!this.isDragging) {
        activeGroup.rotation.y += 0.003;
      }
    }

    if (this.currentMode === "cardio" && this.cardioCore) {
      const s = 1.0 + Math.sin(Date.now() * 0.006) * 0.08;
      this.cardioCore.scale.set(s, s, s);
    }

    this.renderer.render(this.scene, this.camera);
  }
}

window.Clinical3DVisualizer = Clinical3DVisualizer;
