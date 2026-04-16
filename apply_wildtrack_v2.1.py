#!/usr/bin/env python3
"""
WILDTRACK v2.1 — Patch script
Aplica los 4 cambios al index.html del servidor.
Ejecutar en el servidor: python3 apply_wildtrack_v2.1.py
"""

import re, shutil, datetime

SRC = '/var/www/wildtrack/index.html'
BAK = f'/var/www/wildtrack/index_backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.html'

# Backup
shutil.copy2(SRC, BAK)
print(f'Backup: {BAK}')

with open(SRC, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# ─────────────────────────────────────────────────────────────────────────────
# CAMBIO 1 — iOS optimizations: meta tags + fix input zoom (font-size 16px)
# ─────────────────────────────────────────────────────────────────────────────

# 1a. Cambiar viewport para incluir safe-area y viewport-fit
html = html.replace(
    'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no',
    'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover'
)

# 1b. Agregar metas iOS faltantes después de apple-touch-icon
APPLE_ICON = '  <link rel="apple-touch-icon" href="icon-192.png">'
if 'format-detection' not in html and APPLE_ICON in html:
    html = html.replace(
        APPLE_ICON,
        APPLE_ICON + '\n  <meta name="format-detection" content="telephone=no,email=no,address=no">\n  <meta name="mobile-web-app-capable" content="yes">'
    )
    print('✓ Meta iOS agregados')

# 1c. Fix: login-input font-size 16px para evitar zoom en iOS
html = html.replace(
    '.login-input {\n      width: 100%; padding: 13px 16px;\n      background: rgba(255,255,255,0.1);\n      border: 1.5px solid rgba(255,255,255,0.2);\n      border-radius: 12px; color: white;\n      font-family: var(--font); font-size: 14px;',
    '.login-input {\n      width: 100%; padding: 13px 16px;\n      background: rgba(255,255,255,0.1);\n      border: 1.5px solid rgba(255,255,255,0.2);\n      border-radius: 12px; color: white;\n      font-family: var(--font); font-size: 16px;'
)

# 1d. -webkit-overflow-scrolling en pantallas scrollables
html = html.replace(
    '#screen-units {\n      overflow-y: auto;',
    '#screen-units {\n      overflow-y: auto; -webkit-overflow-scrolling: touch;'
)
html = html.replace(
    '#screen-history { overflow-y: auto; padding: 12px; }',
    '#screen-history { overflow-y: auto; -webkit-overflow-scrolling: touch; padding: 12px; }'
)
html = html.replace(
    '#screen-reports { overflow-y: auto; padding: 12px; }',
    '#screen-reports { overflow-y: auto; -webkit-overflow-scrolling: touch; padding: 12px; }'
)
html = html.replace(
    '#screen-alerts { overflow-y: auto; padding: 12px 12px 100px; }',
    '#screen-alerts { overflow-y: auto; -webkit-overflow-scrolling: touch; padding: 12px 12px 100px; }'
)
print('✓ iOS scroll y font-size corregidos')

# ─────────────────────────────────────────────────────────────────────────────
# CAMBIO 2 — CSS: estilos para banner PWA, botón navegación, marcador usuario
# ─────────────────────────────────────────────────────────────────────────────

NEW_CSS = """
    /* ── PWA INSTALL BANNER ── */
    #pwa-banner {
      position: fixed; bottom: 0; left: 0; right: 0; z-index: 99990;
      background: linear-gradient(135deg, var(--navy2), var(--navy));
      color: white; padding: 14px 16px;
      padding-bottom: calc(14px + env(safe-area-inset-bottom, 0px));
      box-shadow: 0 -4px 24px rgba(26,61,143,0.35);
      display: none; flex-direction: column; gap: 10px;
      animation: slideUp 0.4s ease;
    }
    #pwa-banner.visible { display: flex; }
    .pwa-banner-row1 { display: flex; align-items: center; gap: 12px; }
    .pwa-banner-icon {
      width: 44px; height: 44px; border-radius: 12px; flex-shrink: 0;
      background: white; display: flex; align-items: center; justify-content: center;
    }
    .pwa-banner-text { flex: 1; }
    .pwa-banner-title { font-size: 13px; font-weight: 800; letter-spacing: 0.5px; }
    .pwa-banner-sub { font-size: 11px; color: rgba(255,255,255,0.7); margin-top: 2px; line-height: 1.4; }
    .pwa-banner-close {
      border: none; background: rgba(255,255,255,0.15); color: white;
      border-radius: 8px; padding: 6px 10px; font-size: 14px; cursor: pointer; flex-shrink: 0;
    }
    .pwa-banner-steps {
      background: rgba(255,255,255,0.12); border-radius: 10px;
      padding: 10px 12px; font-size: 11px; line-height: 1.8;
      color: rgba(255,255,255,0.9); display: none;
    }
    .pwa-banner-steps.show { display: block; }
    .pwa-banner-btn {
      width: 100%; padding: 12px; background: white; color: var(--navy);
      border: none; border-radius: 12px; font-family: var(--font);
      font-size: 13px; font-weight: 800; cursor: pointer; letter-spacing: 0.5px;
    }
    .pwa-banner-btn:active { opacity: 0.88; }

    /* ── BOTÓN NAVEGAR AL VEHÍCULO ── */
    #btn-nav-vehicle {
      position: absolute; top: 12px; right: 12px; z-index: 600;
      background: white; border: none; border-radius: 14px;
      padding: 10px 14px; font-family: var(--font);
      font-size: 12px; font-weight: 700; color: var(--navy);
      box-shadow: var(--shadow-lg); cursor: pointer;
      display: none; align-items: center; gap: 6px;
      transition: all 0.2s;
    }
    #btn-nav-vehicle.visible { display: flex; }
    #btn-nav-vehicle:active { transform: scale(0.96); background: var(--blue-light); }

    /* ── SHEET NAVEGACIÓN ── */
    #nav-sheet-overlay {
      position: fixed; inset: 0; z-index: 9500;
      background: rgba(15,45,110,0.6); backdrop-filter: blur(4px);
      display: none; align-items: flex-end;
    }
    #nav-sheet-overlay.open { display: flex; }
    #nav-sheet {
      width: 100%; background: white; border-radius: 24px 24px 0 0;
      padding: 0 0 32px; box-shadow: 0 -8px 40px rgba(26,61,143,0.28);
      animation: slideUp 0.3s ease;
    }
    .nav-sheet-handle { width: 40px; height: 4px; background: #dde6f0; border-radius: 2px; margin: 12px auto 0; }
    .nav-sheet-head {
      padding: 14px 20px 12px; border-bottom: 1px solid #dde6f0;
      display: flex; align-items: center; justify-content: space-between;
    }
    .nav-sheet-title { font-size: 15px; font-weight: 800; color: var(--navy); }
    .nav-sheet-close { border: none; background: #f0f4fa; border-radius: 10px; padding: 7px 10px; font-size: 16px; cursor: pointer; color: var(--muted); }
    .nav-sheet-distances {
      display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
      padding: 14px 20px; border-bottom: 1px solid #f0f4fa;
    }
    .nav-dist-item { background: #f0f4fa; border-radius: 10px; padding: 10px 12px; text-align: center; }
    .nav-dist-lbl { font-size: 9px; color: var(--muted); font-weight: 600; text-transform: uppercase; margin-bottom: 3px; }
    .nav-dist-val { font-family: var(--font-mono); font-size: 16px; font-weight: 800; color: var(--navy); }
    .nav-apps { padding: 14px 20px; display: flex; flex-direction: column; gap: 8px; }
    .nav-app-btn {
      display: flex; align-items: center; gap: 12px;
      padding: 14px 16px; border-radius: 14px; border: 1.5px solid #dde6f0;
      background: white; cursor: pointer; font-family: var(--font);
      transition: all 0.15s; text-decoration: none;
    }
    .nav-app-btn:active { background: var(--blue-light); border-color: var(--blue); }
    .nav-app-ico { font-size: 28px; flex-shrink: 0; }
    .nav-app-name { font-size: 14px; font-weight: 700; color: var(--navy); }
    .nav-app-sub { font-size: 11px; color: var(--muted); margin-top: 1px; }

    /* ── MARCADOR POSICIÓN USUARIO ── */
    .user-location-dot {
      width: 18px; height: 18px; border-radius: 50%;
      background: #2B4DE8; border: 3px solid white;
      box-shadow: 0 0 0 4px rgba(43,77,232,0.25), 0 2px 8px rgba(43,77,232,0.4);
      animation: userPulse 2s infinite;
    }
    @keyframes userPulse {
      0%,100% { box-shadow: 0 0 0 4px rgba(43,77,232,0.25), 0 2px 8px rgba(43,77,232,0.4); }
      50%      { box-shadow: 0 0 0 10px rgba(43,77,232,0.08), 0 2px 8px rgba(43,77,232,0.4); }
    }
"""

# Insertar antes de cierre de </style>
if '/* ── PWA INSTALL BANNER ── */' not in html:
    html = html.replace('  </style>', NEW_CSS + '\n  </style>')
    print('✓ CSS nuevo insertado')

# ─────────────────────────────────────────────────────────────────────────────
# CAMBIO 3 — HTML: PWA banner + botón navegar en pantalla mapa
# ─────────────────────────────────────────────────────────────────────────────

PWA_BANNER_HTML = """
<!-- PWA INSTALL BANNER -->
<div id="pwa-banner">
  <div class="pwa-banner-row1">
    <div class="pwa-banner-icon">
      <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="32" height="32">
        <rect width="100" height="100" rx="22" fill="#2B4DE8"/>
        <polygon points="50,14 73,73 50,60 27,73" fill="white" opacity="0.97"/>
        <polygon points="50,60 27,73 50,54" fill="rgba(0,0,0,0.15)"/>
        <circle cx="78" cy="22" r="18" fill="white"/>
        <text x="78" y="28" text-anchor="middle" fill="#2B4DE8" font-family="Montserrat,sans-serif" font-size="16" font-weight="800">W</text>
      </svg>
    </div>
    <div class="pwa-banner-text">
      <div class="pwa-banner-title">Instala WILDTRACK</div>
      <div class="pwa-banner-sub" id="pwa-banner-sub">Acceso rápido desde tu pantalla de inicio</div>
    </div>
    <button class="pwa-banner-close" onclick="dismissPWABanner()">✕</button>
  </div>
  <div class="pwa-banner-steps" id="pwa-banner-steps"></div>
  <button class="pwa-banner-btn" id="pwa-banner-btn" onclick="handlePWAInstall()">Instalar aplicación</button>
</div>
"""

NAV_BUTTON_HTML = """      <button id="btn-nav-vehicle" onclick="openNavSheet()" title="Navegar al vehículo">
        🧭 <span>Ir al vehículo</span>
      </button>"""

NAV_SHEET_HTML = """
<!-- SHEET NAVEGACIÓN AL VEHÍCULO -->
<div id="nav-sheet-overlay" onclick="if(event.target.id==='nav-sheet-overlay')closeNavSheet()">
  <div id="nav-sheet">
    <div class="nav-sheet-handle"></div>
    <div class="nav-sheet-head">
      <span class="nav-sheet-title">🧭 Navegar al vehículo</span>
      <button class="nav-sheet-close" onclick="closeNavSheet()">✕</button>
    </div>
    <div class="nav-sheet-distances">
      <div class="nav-dist-item">
        <div class="nav-dist-lbl">Distancia</div>
        <div class="nav-dist-val" id="nav-dist-km">—</div>
      </div>
      <div class="nav-dist-item">
        <div class="nav-dist-lbl">Vehículo</div>
        <div class="nav-dist-val" id="nav-vehicle-name" style="font-size:11px;">—</div>
      </div>
    </div>
    <div class="nav-apps" id="nav-apps-list">
      <div style="text-align:center;padding:16px;color:var(--muted);font-size:13px;">Obteniendo tu ubicación...</div>
    </div>
  </div>
</div>
"""

# Insertar banner PWA después de <!-- LOGIN SCREEN -->
if 'pwa-banner' not in html:
    html = html.replace(
        '\n<!-- LOGIN SCREEN -->',
        '\n' + PWA_BANNER_HTML + '\n<!-- LOGIN SCREEN -->'
    )
    print('✓ Banner PWA HTML insertado')

# Insertar botón navegar en screen-map (después de map-back-btn)
if 'btn-nav-vehicle' not in html:
    html = html.replace(
        '    <button id="map-back-btn" onclick="volverAUnidades()">← Volver</button>\n    <div id="map"></div>',
        '    <button id="map-back-btn" onclick="volverAUnidades()">← Volver</button>\n' + NAV_BUTTON_HTML + '\n    <div id="map"></div>'
    )
    print('✓ Botón navegar HTML insertado')

# Insertar sheet de navegación antes del cierre de body
if 'nav-sheet-overlay' not in html:
    html = html.replace('\n<script>', NAV_SHEET_HTML + '\n<script>', 1)
    print('✓ Sheet navegación HTML insertado')

# ─────────────────────────────────────────────────────────────────────────────
# CAMBIO 4 — JS: Fix heading rotation en syncMarkers
# ─────────────────────────────────────────────────────────────────────────────

# 4a. Agregar setIcon en syncMarkers para que la flecha gire con cada update
OLD_SYNC = '''  vehicles.forEach(function(v) {
    if (markers[v.id]) {
      markers[v.id].setLatLng([v.lat, v.lng]);
      if (markers[v.id].isPopupOpen()) {
        markers[v.id].setPopupContent(makePopup(v));
      }
    } else if (mapReady && map) {'''

NEW_SYNC = '''  vehicles.forEach(function(v) {
    if (markers[v.id]) {
      markers[v.id].setLatLng([v.lat, v.lng]);
      markers[v.id].setIcon(makeIcon(v)); // actualiza heading (brújula)
      if (markers[v.id].isPopupOpen()) {
        markers[v.id].setPopupContent(makePopup(v));
      }
    } else if (mapReady && map) {'''

if OLD_SYNC in html:
    html = html.replace(OLD_SYNC, NEW_SYNC)
    print('✓ Heading rotation fix aplicado en syncMarkers')
else:
    print('⚠ syncMarkers — cadena no encontrada, revisar manualmente')

# ─────────────────────────────────────────────────────────────────────────────
# CAMBIO 5 — JS: PWA install banner + Navegación al vehículo
# ─────────────────────────────────────────────────────────────────────────────

NEW_JS = """
// ─────────────────────────────────────────────────
// PWA INSTALL BANNER
// ─────────────────────────────────────────────────
var _deferredPWAPrompt = null;
var _isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
var _isInStandalone = window.matchMedia('(display-mode: standalone)').matches || navigator.standalone;

window.addEventListener('beforeinstallprompt', function(e) {
  e.preventDefault();
  _deferredPWAPrompt = e;
  showPWABannerIfNeeded();
});

function showPWABannerIfNeeded() {
  if (_isInStandalone) return; // ya instalada
  if (localStorage.getItem('wt_pwa_dismissed')) return;
  var banner = document.getElementById('pwa-banner');
  if (!banner) return;
  if (_isIOS) {
    // iOS no soporta beforeinstallprompt — instrucciones manuales
    document.getElementById('pwa-banner-sub').textContent = 'Instala en tu iPhone para acceso sin browser';
    var steps = document.getElementById('pwa-banner-steps');
    steps.innerHTML = '1️⃣ Toca el botón <strong>Compartir</strong> ⬆️ en Safari<br>2️⃣ Selecciona <strong>Añadir a pantalla de inicio</strong><br>3️⃣ Toca <strong>Añadir</strong> — ¡listo!';
    steps.classList.add('show');
    document.getElementById('pwa-banner-btn').textContent = 'Entendido ✓';
    document.getElementById('pwa-banner-btn').onclick = function() { dismissPWABanner(); };
    setTimeout(function() { banner.classList.add('visible'); }, 1800);
  } else if (_deferredPWAPrompt) {
    setTimeout(function() { banner.classList.add('visible'); }, 1800);
  }
}

function handlePWAInstall() {
  if (_isIOS) { dismissPWABanner(); return; }
  if (!_deferredPWAPrompt) return;
  _deferredPWAPrompt.prompt();
  _deferredPWAPrompt.userChoice.then(function(r) {
    if (r.outcome === 'accepted') dismissPWABanner();
    _deferredPWAPrompt = null;
  });
}

function dismissPWABanner() {
  var banner = document.getElementById('pwa-banner');
  if (banner) banner.classList.remove('visible');
  localStorage.setItem('wt_pwa_dismissed', '1');
}

// Mostrar banner al cargar si es iOS
window.addEventListener('load', function() {
  if (_isIOS && !_isInStandalone) showPWABannerIfNeeded();
});

// ─────────────────────────────────────────────────
// NAVEGACIÓN AL VEHÍCULO (Ir al vehículo)
// ─────────────────────────────────────────────────
var _userLat = null, _userLng = null, _userMarker = null;

function openNavSheet() {
  var v = vehicles.find(function(x) { return x.id === selectedId; });
  if (!v) return;
  document.getElementById('nav-vehicle-name').textContent = v.name;
  document.getElementById('nav-dist-km').textContent = '…';
  document.getElementById('nav-apps-list').innerHTML =
    '<div style="text-align:center;padding:20px;color:var(--muted);font-size:13px;">📡 Obteniendo tu ubicación...</div>';
  document.getElementById('nav-sheet-overlay').classList.add('open');

  if (!navigator.geolocation) {
    document.getElementById('nav-apps-list').innerHTML =
      '<div style="text-align:center;padding:16px;color:#dc2626;font-size:13px;">⚠️ Geolocalización no disponible en este dispositivo</div>';
    return;
  }

  navigator.geolocation.getCurrentPosition(function(pos) {
    _userLat = pos.coords.latitude;
    _userLng = pos.coords.longitude;

    // Mostrar marcador de usuario en el mapa
    if (map && mapReady) {
      if (_userMarker) map.removeLayer(_userMarker);
      _userMarker = L.marker([_userLat, _userLng], {
        icon: L.divIcon({
          className: '',
          html: '<div class="user-location-dot"></div>',
          iconSize: [18, 18], iconAnchor: [9, 9]
        }),
        zIndexOffset: 1000
      }).addTo(map);
      _userMarker.bindPopup('<div style="font-size:12px;font-weight:700;color:#2B4DE8;">📍 Tu ubicación</div>', {
        className: 'wt-popup', closeButton: false, autoPan: false
      });
      // Ajustar vista para ver ambos puntos
      var bounds = L.latLngBounds([[_userLat, _userLng], [v.lat, v.lng]]);
      map.fitBounds(bounds, { padding: [60, 60], animate: true });
    }

    // Calcular distancia
    var distKm = haversineKm(_userLat, _userLng, v.lat, v.lng);
    var distStr = distKm < 1
      ? Math.round(distKm * 1000) + ' m'
      : distKm.toFixed(1) + ' km';
    document.getElementById('nav-dist-km').textContent = distStr;

    // Construir URLs de navegación
    var origin = _userLat + ',' + _userLng;
    var dest   = v.lat + ',' + v.lng;
    var label  = encodeURIComponent(v.name);

    var gMapsUrl   = 'https://www.google.com/maps/dir/?api=1&origin=' + origin + '&destination=' + dest + '&travelmode=driving';
    var appleMapsUrl = 'https://maps.apple.com/?saddr=' + origin + '&daddr=' + dest + '&dirflg=d';
    var wazeUrl    = 'https://waze.com/ul?ll=' + dest + '&navigate=yes&z=10';
    var osmUrl     = 'https://www.openstreetmap.org/directions?engine=graphhopper_car&route=' + origin + ';' + dest;

    var isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
    var mapsOrder = isIOS
      ? [ {url: appleMapsUrl, ico: '🗺', name: 'Apple Maps', sub: 'Navegación nativa iOS'},
          {url: gMapsUrl,     ico: '🟢', name: 'Google Maps', sub: 'Ruta en tiempo real'},
          {url: wazeUrl,      ico: '💙', name: 'Waze', sub: 'Tráfico y alertas'},
          {url: osmUrl,       ico: '🌍', name: 'OpenStreetMap', sub: 'Sin cuenta requerida'} ]
      : [ {url: gMapsUrl,     ico: '🟢', name: 'Google Maps', sub: 'Ruta en tiempo real'},
          {url: wazeUrl,      ico: '💙', name: 'Waze', sub: 'Tráfico y alertas'},
          {url: appleMapsUrl, ico: '🗺', name: 'Apple Maps', sub: 'Requiere iOS/macOS'},
          {url: osmUrl,       ico: '🌍', name: 'OpenStreetMap', sub: 'Sin cuenta requerida'} ];

    document.getElementById('nav-apps-list').innerHTML = mapsOrder.map(function(app) {
      return '<a href="' + app.url + '" target="_blank" class="nav-app-btn">' +
        '<span class="nav-app-ico">' + app.ico + '</span>' +
        '<div><div class="nav-app-name">' + app.name + '</div>' +
        '<div class="nav-app-sub">' + app.sub + '</div></div>' +
        '<span style="margin-left:auto;color:var(--muted);font-size:18px;">›</span>' +
        '</a>';
    }).join('');

  }, function(err) {
    var msg = err.code === 1
      ? '⚠️ Permiso de ubicación denegado. Actívalo en los ajustes del navegador.'
      : '⚠️ No se pudo obtener tu ubicación. Verifica la señal GPS.';
    document.getElementById('nav-apps-list').innerHTML =
      '<div style="padding:16px;color:#dc2626;font-size:12px;font-weight:600;line-height:1.5;">' + msg + '</div>';
  }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 });
}

function closeNavSheet() {
  document.getElementById('nav-sheet-overlay').classList.remove('open');
}

// Mostrar/ocultar botón navegar según modo mapa
function updateNavBtn() {
  var btn = document.getElementById('btn-nav-vehicle');
  if (!btn) return;
  if (mapMode === 'unit' && selectedId) {
    btn.classList.add('visible');
  } else {
    btn.classList.remove('visible');
    // Limpiar marcador usuario si había
    if (_userMarker && map) {
      try { map.removeLayer(_userMarker); } catch(e){}
      _userMarker = null;
    }
  }
}
"""

# Insertar el nuevo JS antes del cierre de </script>
if 'openNavSheet' not in html:
    html = html.replace('\n</script>\n</body>', NEW_JS + '\n</script>\n</body>')
    print('✓ JS navegación y PWA banner insertados')

# ─────────────────────────────────────────────────────────────────────────────
# CAMBIO 6 — Llamar updateNavBtn() cuando el modo cambia
# ─────────────────────────────────────────────────────────────────────────────

# Llamar updateNavBtn después de cambiar mapMode en openUnit
old_open_unit_badge = '''  document.getElementById('map-back-btn').style.display = 'block';
  document.getElementById('rastreando-badge').style.display = 'flex';'''
new_open_unit_badge = '''  document.getElementById('map-back-btn').style.display = 'block';
  document.getElementById('rastreando-badge').style.display = 'flex';
  updateNavBtn();'''

if old_open_unit_badge in html and 'updateNavBtn' not in html.split('openUnit')[1].split('function')[0]:
    html = html.replace(old_open_unit_badge, new_open_unit_badge)
    print('✓ updateNavBtn() conectado a openUnit')

# Llamar updateNavBtn al volver
old_volver = '''function volverAUnidades() {
  stopTracking();
  mapMode = 'all';
  selectedId = null;
  document.getElementById('map-back-btn').style.display = 'none';
  document.getElementById('rastreando-badge').style.display = 'none';'''
new_volver = '''function volverAUnidades() {
  stopTracking();
  mapMode = 'all';
  selectedId = null;
  document.getElementById('map-back-btn').style.display = 'none';
  document.getElementById('rastreando-badge').style.display = 'none';
  updateNavBtn();'''

if old_volver in html:
    html = html.replace(old_volver, new_volver)
    print('✓ updateNavBtn() conectado a volverAUnidades')

# ─────────────────────────────────────────────────────────────────────────────
# Guardar
# ─────────────────────────────────────────────────────────────────────────────
with open(SRC, 'w', encoding='utf-8') as f:
    f.write(html)

new_len = len(html)
print(f'\n✅ Completado. {original_len} → {new_len} chars (+{new_len - original_len})')
print(f'   Backup en: {BAK}')
print(f'\nRecarga la app con Ctrl+Shift+R')
