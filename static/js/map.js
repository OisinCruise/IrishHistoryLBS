let map;
let allSites = [];
let markers = {};
let markerLayer;
let searchMode = false;
let searchCircle = null;
let searchMarker = null;
let currentSiteId = null;
let countyBoundaryLayer = null;
let countyPolygons = {};
let boundariesVisible = true;

// Color palette for county boundaries
const countyColors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#A3E4D7',
    '#F1948A', '#85C1E2', '#F7DC6F', '#D7BDE2', '#A9DFBF',
    '#F8B88B', '#AED6F1', '#F1948A', '#D5A6BD', '#FAD7A0',
    '#85C1E2', '#F7DC6F', '#BB8FCE', '#A9CCE3', '#F8B88B',
    '#F1948A', '#AED6F1'
];

let countyColorIndex = 0;
const countyColorMap = {};

function showAlert(message, type = 'info') {
    const colors = {
        'success': '#28a745',
        'info': '#17a2b8',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'secondary': '#6c757d'
    };

    document.querySelectorAll('[data-alert-id]').forEach(el => el.remove());

    const wrapper = document.createElement('div');
    wrapper.setAttribute('data-alert-id', 'lbs-' + Date.now());
    wrapper.style.cssText = `position:fixed!important;top:20px!important;left:50%!important;transform:translateX(-50%)!important;z-index:2147483647!important;width:auto!important;max-width:600px!important;min-width:300px!important`;

    const alertDiv = document.createElement('div');
    alertDiv.style.cssText = `background-color:${colors[type]||colors['info']}!important;color:white!important;padding:12px 20px!important;border-radius:4px!important;box-shadow:0 4px 12px rgba(0,0,0,.5)!important;font-size:14px!important;font-weight:500!important;text-align:center!important;border:none!important;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial!important;line-height:1.5!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:10px!important`;
    alertDiv.textContent = message;

    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '✕';
    closeBtn.style.cssText = `background:rgba(255,255,255,.3)!important;border:1px solid rgba(255,255,255,.5)!important;color:white!important;padding:2px 6px!important;border-radius:3px!important;cursor:pointer!important;font-size:16px!important;line-height:1!important;margin-left:10px!important`;
    closeBtn.onclick = () => wrapper.remove();

    alertDiv.appendChild(closeBtn);
    wrapper.appendChild(alertDiv);
    document.body.appendChild(wrapper);

    setTimeout(() => {if(wrapper&&wrapper.parentNode)wrapper.remove()},4000);
}

function setMapCursor(mode) {
    const mapEl = document.getElementById('map');
    if (!mapEl) return;

    if (mode === 'crosshair') {
        mapEl.classList.add('crosshair-cursor');
        mapEl.classList.add('search-mode');
    } else {
        mapEl.classList.remove('crosshair-cursor');
        mapEl.classList.remove('search-mode');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    loadCountyBoundaries();
    loadSites();
    setupEventListeners();
});

function initializeMap() {
    const irishCenter = [53.3498, -6.2603];
    const zoom = 7;

    map = L.map('map', {
        tap: true,
        tapTolerance: 15
    }).setView(irishCenter, zoom);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
        minZoom: 5
    }).addTo(map);

    markerLayer = L.layerGroup().addTo(map);
    L.control.scale({position: 'bottomright', imperial: false}).addTo(map);

    setMapCursor('pointer');

    map.on('click', function(e) {
        if (searchMode) {
            const radiusKm = parseFloat(document.getElementById('radius-input')?.value || 50);
            const lat = e.latlng.lat;
            const lng = e.latlng.lng;
            performProximitySearch(lat, lng, radiusKm);
        } else {
            const lat = e.latlng.lat.toFixed(6);
            const lng = e.latlng.lng.toFixed(6);
            showAlert(`Coordinates: ${lat}, ${lng}`, 'info');

            const marker = L.circleMarker([lat, lng], {
                radius: 9,
                color: "#3498db",
                fillColor: "#3498db",
                fillOpacity: 0.3,
                opacity: 0.9
            }).addTo(map);

            setTimeout(() => map.removeLayer(marker), 750);
        }
    });
}

// Fetch and display county boundaries as colored polygons
function loadCountyBoundaries() {
    fetch('/api/county-boundaries/geojson_with_colors/')
        .then(r => r.json())
        .then(data => {
            console.log(`Loaded ${data.features.length} county boundaries`);

            countyBoundaryLayer = L.geoJSON(data, {
                style: function(feature) {
                    const color = feature.properties.color;
                    const countyName = feature.properties.name;

                    countyColorMap[countyName.toLowerCase()] = color;

                    return {
                        color: color,
                        weight: 2.5,
                        opacity: 0.8,
                        fillOpacity: 0.15,
                        dashArray: '4, 4'
                    };
                },
                onEachFeature: function(feature, layer) {
                    const countyName = feature.properties.name;
                    
                    layer.bindPopup(`
                        <div style="text-align: center;">
                            <strong>${countyName} County</strong><br>
                            <small style="color: #666;">Click filter button to show sites</small>
                        </div>
                    `);

                    // Highlight on hover
                    layer.on('mouseover', function() {
                        this.setStyle({
                            weight: 3.5,
                            opacity: 1,
                            fillOpacity: 0.25
                        });
                        this.bringToFront();
                    });

                    layer.on('mouseout', function() {
                        this.setStyle({
                            weight: 2.5,
                            opacity: 0.8,
                            fillOpacity: 0.15
                        });
                    });
                }
            }).addTo(map);

            countyPolygons = countyBoundaryLayer;
            showAlert('County boundaries loaded with colored borders', 'success');
        })
        .catch(error => {
            console.error('Error loading county boundaries:', error);
            showAlert('Error loading county boundaries', 'warning');
        });
}

// Toggle county boundary visibility
function toggleCountyBoundaries() {
    const btn = document.getElementById('toggle-boundaries');
    if (!btn || !countyBoundaryLayer) return;

    boundariesVisible = !boundariesVisible;

    if (boundariesVisible) {
        map.addLayer(countyBoundaryLayer);
        btn.classList.remove('btn-outline-secondary');
        btn.classList.add('btn-secondary');
        btn.innerHTML = '<i class="fas fa-eye-slash me-1"></i>Hide Boundaries';
        showAlert('County boundaries visible', 'info');
    } else {
        map.removeLayer(countyBoundaryLayer);
        btn.classList.remove('btn-secondary');
        btn.classList.add('btn-outline-secondary');
        btn.innerHTML = '<i class="fas fa-eye me-1"></i>Show Boundaries';
        showAlert('County boundaries hidden', 'info');
    }
}

async function loadSites() {
    try {
        const apiUrl = window.DJANGO_CONTEXT.apiBaseUrl;
        const response = await fetch(apiUrl);

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        allSites = data;

        console.log(`Loaded ${allSites.length} sites`);
        displaySites(allSites);
        updateStatistics();
        showAlert(`Loaded ${allSites.length} historical sites`, 'success');
    } catch (error) {
        console.error('Error loading sites:', error);
        showAlert('Error loading historical sites: ' + error.message, 'danger');
    }
}

function displaySites(sites) {
    markerLayer.clearLayers();
    markers = {};

    sites.forEach(site => {
        const lat = site.latitude;
        const lng = site.longitude;
        const color = getCategoryColor(site.category);

        const marker = L.circleMarker([lat, lng], {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });

        const popupContent = createPopupContent(site);
        marker.bindPopup(popupContent);
        marker.addTo(markerLayer);
        markers[site.id] = marker;

        marker.on('click', function() {
            currentSiteId = site.id;
            showSiteModal(site);
        });
    });
}

function getCategoryColor(category) {
    const colors = {
        'EASTER_RISING': '#E74C3C',
        'WAR_INDEPENDENCE': '#3498DB',
        'TREATY': '#F39C12',
        'CIVIL_WAR': '#C0392B',
        'AFTERMATH': '#27AE60'
    };
    return colors[category] || '#95A5A6';
}

function createPopupContent(site) {
    const date = new Date(site.event_date);
    const significance = site.significance || 'No description available';
    const significancePreview = significance.length > 100 ?
        significance.substring(0, 100) + '...' : significance;

    return `
        <div style="font-size: 12px; max-width: 250px;">
            <strong>${site.name}</strong><br>
            <small><strong>Date:</strong> ${date.toLocaleDateString()}</small><br>
            <small><strong>Location:</strong> ${site.location_name}</small><br>
            <small style="color: #666;">${significancePreview}</small>
        </div>
    `;
}

function showSiteModal(site) {
    const modal = document.getElementById('siteModal');
    if (!modal) return;

    document.getElementById('siteModalTitle').textContent = site.name;

    const date = new Date(site.event_date);
    let html = `
        <div>
            <div class="mb-3">
                <h6 class="fw-bold">Date</h6>
                <p>${date.toLocaleDateString()}</p>
            </div>
            <div class="mb-3">
                <h6 class="fw-bold">Location</h6>
                <p>${site.location_name}</p>
            </div>
            <div class="mb-3">
                <h6 class="fw-bold">Category</h6>
                <p><span class="badge" style="background-color: ${getCategoryColor(site.category)};">${site.category}</span></p>
            </div>
            <div class="mb-3">
                <h6 class="fw-bold">Event Type</h6>
                <p>${site.event_type || 'Unknown'}</p>
            </div>
    `;

    if (site.casualties) {
        html += `
            <div class="mb-3">
                <h6 class="fw-bold">Casualties</h6>
                <p>${site.casualties}</p>
            </div>
        `;
    }

    html += `
            <div class="mb-3">
                <h6 class="fw-bold">Significance</h6>
                <p>${site.significance}</p>
            </div>
    `;

    if (site.description) {
        html += `
            <div class="mb-3">
                <h6 class="fw-bold">Description</h6>
                <p>${site.description}</p>
            </div>
        `;
    }

    html += '</div>';

    document.getElementById('siteModalBody').innerHTML = html;

    new bootstrap.Modal(modal).show();
}

async function showRelatedSites() {
    const bufferKm = 20;
    const modal = document.getElementById('relatedSitesModal');

    if (!modal || !currentSiteId) return;

    try {
        const response = await fetch(`/api/sites/buffer_zone/?site_id=${currentSiteId}&buffer_km=${bufferKm}`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        const relatedSites = data.sites;

        document.getElementById('relatedSitesTitle').textContent = `Sites Near ${data.center_site} (within ${bufferKm}km)`;

        let html = relatedSites.length > 0 ? '<ul style="list-style: none; padding: 0;">' : '';

        relatedSites.forEach(site => {
            const date = new Date(site.event_date);
            html += `
                <li style="padding: 10px; border-bottom: 1px solid #eee;">
                    <strong>${site.name}</strong><br>
                    <small><strong>Date:</strong> ${date.toLocaleDateString()}</small><br>
                    <small><strong>Type:</strong> ${site.event_type}</small>
                </li>
            `;
        });

        if (relatedSites.length > 0) html += '</ul>';
        else html = '<p class="text-muted text-center">No related sites found within this buffer zone.</p>';

        document.getElementById('relatedSitesBody').innerHTML = html;

        // Show buffer zone on map
        const currentSite = allSites.find(s => s.id === currentSiteId);
        if (currentSite) {
            if (searchCircle) map.removeLayer(searchCircle);
            searchCircle = L.circle([currentSite.latitude, currentSite.longitude], {
                radius: bufferKm * 1000,
                color: '#17a2b8',
                fillColor: '#17a2b8',
                fillOpacity: 0.1,
                weight: 2,
                dashArray: '5, 5'
            }).addTo(map);
        }

        new bootstrap.Modal(modal).show();
        showAlert(`Showing ${relatedSites.length} related sites`, 'info');
    } catch (error) {
        console.error('Error loading related sites:', error);
        showAlert('Error loading related sites: ' + error.message, 'danger');
    }
}

// County filter using spatial point-in-polygon queries
async function filterByCounty() {
    const countySelect = document.getElementById('county-select');
    const selected = countySelect ? countySelect.value : '';

    if (!selected) {
        displaySites(allSites);
        updateStatistics();
        showAlert('Showing all sites', 'info');
        return;
    }

    // Filter sites using spatial query (ST_Within)
    try {
        const params = new URLSearchParams({county: selected});
        const response = await fetch(`/api/sites/?${params}`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        displaySites(data);
        updateStatistics();
        showAlert(`Showing ${data.length} sites in ${selected}`, 'success');
    } catch (error) {
        console.error('Error filtering by county:', error);
        showAlert('Error filtering by county: ' + error.message, 'danger');
    }
}

function setupEventListeners() {
    // County filter
    const countyBtn = document.getElementById('filter-county');
    if (countyBtn) {
        countyBtn.addEventListener('click', filterByCounty);
    }

    // Toggle boundaries
    const toggleBtn = document.getElementById('toggle-boundaries');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleCountyBoundaries);
    }

    // Category filters
    const categoryBtn = document.getElementById('apply-categories');
    if (categoryBtn) {
        categoryBtn.addEventListener('click', filterByCategory);
    }

    // Timeline filter
    const timelineBtn = document.getElementById('filter-timeline');
    if (timelineBtn) {
        timelineBtn.addEventListener('click', filterByTimeline);
    }

    // Proximity search button
    const searchBtn = document.getElementById('search-nearby');
    if (searchBtn) {
        searchBtn.addEventListener('click', searchNearby);
    }

    // Show all sites button
    const showAllBtn = document.getElementById('reset-search');
    if (showAllBtn) {
        showAllBtn.addEventListener('click', function() {
            displaySites(allSites);
            if (searchCircle) map.removeLayer(searchCircle);
            if (searchMarker) map.removeLayer(searchMarker);
            searchCircle = null;
            searchMarker = null;

            const countySelect = document.getElementById('county-select');
            if (countySelect) countySelect.value = '';

            cancelSearchMode();
            updateStatistics();
        });
    }

    // Related sites button
    const relatedBtn = document.getElementById('show-related-sites');
    if (relatedBtn) {
        relatedBtn.addEventListener('click', showRelatedSites);
    }
}

function filterByCategory() {
    const selected = Array.from(document.querySelectorAll('.category-filter:checked'))
        .map(el => el.value);

    if (selected.length === 0) {
        displaySites(allSites);
        updateStatistics();
        showAlert('Showing all sites', 'info');
        return;
    }

    const filtered = allSites.filter(site => selected.includes(site.category));
    displaySites(filtered);
    updateStatistics();
    showAlert(`Showing ${filtered.length} sites`, 'info');
}

function filterByTimeline() {
    const startDate = new Date(document.getElementById('start-date').value);
    const endDate = new Date(document.getElementById('end-date').value);

    const filtered = allSites.filter(site => {
        const siteDate = new Date(site.event_date);
        return siteDate >= startDate && siteDate <= endDate;
    });

    displaySites(filtered);
    updateStatistics();
    showAlert(`Showing ${filtered.length} sites in date range`, 'info');
}

function searchNearby() {
    if (!searchMode) {
        searchMode = true;
        const btn = document.getElementById('search-nearby');
        btn.textContent = 'Cancel Search';
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-danger');
        showAlert('Click anywhere on the map to set search center', 'info');
        setMapCursor('crosshair');
    } else {
        cancelSearchMode();
    }
}

function cancelSearchMode() {
    searchMode = false;
    const btn = document.getElementById('search-nearby');
    btn.textContent = 'Start Search';
    btn.classList.remove('btn-danger');
    btn.classList.add('btn-primary');
    setMapCursor('pointer');

    if (searchCircle) {
        map.removeLayer(searchCircle);
        searchCircle = null;
    }

    if (searchMarker) {
        map.removeLayer(searchMarker);
        searchMarker = null;
    }

    displaySites(allSites);
    updateStatistics();
    showAlert('Search cancelled', 'secondary');
}

async function performProximitySearch(lat, lng, radiusKm) {
    try {
        const response = await fetch('/api/sites/nearby/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.DJANGO_CONTEXT.csrfToken
            },
            body: JSON.stringify({
                lat: lat,
                lng: lng,
                radius_km: radiusKm
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        displaySites(data.sites);
        updateStatistics();

        if (searchCircle) {
            map.removeLayer(searchCircle);
        }

        searchCircle = L.circle([lat, lng], {
            radius: radiusKm * 1000,
            color: '#3498DB',
            fillColor: '#3498DB',
            fillOpacity: 0.1,
            weight: 2
        }).addTo(map);

        if (searchMarker) {
            map.removeLayer(searchMarker);
        }

        searchMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'search-center-icon',
                html: '',
                iconSize: [20, 20]
            })
        }).addTo(map);

        searchMode = false;
        const btn = document.getElementById('search-nearby');
        btn.textContent = 'Start Search';
        btn.classList.remove('btn-danger');
        btn.classList.add('btn-primary');
        setMapCursor('pointer');

        showAlert(`Found ${data.sites.length} sites within ${radiusKm}km`, 'success');
    } catch (error) {
        console.error('Proximity search error:', error);
        showAlert('Error performing proximity search: ' + error.message, 'danger');
        cancelSearchMode();
    }
}

function updateStatistics() {
    const totalEl = document.getElementById('stat-total');
    const visibleEl = document.getElementById('stat-visible');

    if (totalEl) totalEl.textContent = allSites.length;
    if (visibleEl) visibleEl.textContent = Object.keys(markers).length;
}
