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

// Fetch and display county boundaries as polygons
function loadCountyBoundaries() {
    fetch('/api/county-boundaries/')
        .then(r => r.json())
        .then(data => {
            console.log(`Loaded ${data.length} county boundaries`);
            data.forEach(county => {
                try {
                    const geojson = JSON.parse(county.geometry);
                    const layer = L.geoJSON(geojson, {
                        style: {
                            color: '#3498DB',
                            weight: 2,
                            opacity: 0.4,
                            fillOpacity: 0.1
                        },
                        onEachFeature: (feature, layer) => {
                            layer.bindPopup(`<strong>${county.name}</strong>`);
                        }
                    }).addTo(map);
                    countyPolygons[county.name.toLowerCase()] = layer;
                } catch (e) {
                    console.error(`Error loading geometry for ${county.name}:`, e);
                }
            });
            showAlert('County boundaries loaded', 'success');
        })
        .catch(error => {
            console.error('Error loading county boundaries:', error);
            showAlert('Error loading county boundaries', 'warning');
        });
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
        <div class="popup-content">
            <h6 class="mb-2">${site.name}</h6>
            <p class="mb-1"><strong>Date:</strong> ${date.toLocaleDateString()}</p>
            <p class="mb-1"><strong>Location:</strong> ${site.location_name}</p>
            <p class="mb-0"><small>${significancePreview}</small></p>
        </div>
    `;
}

function showSiteModal(site) {
    const date = new Date(site.event_date);
    const modal = document.getElementById('siteModal');
    
    document.getElementById('siteModalTitle').textContent = site.name;
    document.getElementById('siteModalBody').innerHTML = `
        <div class="mb-3">
            <p><strong>Date:</strong> ${date.toLocaleDateString()}</p>
            <p><strong>Location:</strong> ${site.location_name}</p>
            <p><strong>Category:</strong> <span class="badge" style="background-color: ${getCategoryColor(site.category)}">${site.category}</span></p>
            <p><strong>Event Type:</strong> ${site.event_type}</p>
            ${site.casualties ? `<p><strong>Casualties:</strong> ${site.casualties}</p>` : ''}
        </div>
        <div>
            <h6>Significance</h6>
            <p>${site.significance}</p>
        </div>
        ${site.description ? `
        <div>
            <h6>Details</h6>
            <p>${site.description}</p>
        </div>
        ` : ''}
    `;
    
    new bootstrap.Modal(modal).show();
}

async function showRelatedSites() {
    if (!currentSiteId) return;
    
    try {
        const bufferKm = 20;
        const response = await fetch(`/api/sites/buffer_zone/?site_id=${currentSiteId}&buffer_km=${bufferKm}`);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        const relatedSites = data.sites;
        
        const modal = document.getElementById('relatedSitesModal');
        document.getElementById('relatedSitesTitle').textContent = `Related Sites within ${bufferKm}km`;
        
        let html = `<p class="text-muted">Found <strong>${relatedSites.length}</strong> sites within ${bufferKm}km</p>`;
        
        if (relatedSites.length > 0) {
            html += '<div class="list-group">';
            relatedSites.forEach(site => {
                const date = new Date(site.event_date);
                html += `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1">${site.name}</h6>
                                <p class="mb-1"><small><strong>Date:</strong> ${date.toLocaleDateString()}</small></p>
                                <p class="mb-0"><small><strong>Type:</strong> ${site.event_type}</small></p>
                            </div>
                            <span class="badge" style="background-color: ${getCategoryColor(site.category)};">${site.category}</span>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        } else {
            html += '<p class="text-muted">No related sites found within this buffer zone.</p>';
        }
        
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
    
    // Show/hide polygons
    Object.entries(countyPolygons).forEach(([name, layer]) => {
        if (!selected || name === selected) {
            layer.setStyle({fillOpacity: 0.2});
        } else {
            layer.setStyle({fillOpacity: 0.05});
        }
    });
    
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
            // Reset county polygon opacity
            Object.values(countyPolygons).forEach(layer => {
                layer.setStyle({fillOpacity: 0.1});
            });
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
                html: '<div style="background: #3498DB; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 5px rgba(0,0,0,0.5);"></div>',
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
