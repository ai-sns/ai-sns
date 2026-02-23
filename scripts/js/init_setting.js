// todo optimize and adjust order
// Initialize settings

// Define a function that sets the corresponding ✓ based on set_route_flag
function initRouteDisplay() {

    const randomRouteItem = document.getElementById("random_route");
    const specifiedRouteItem = document.getElementById("specified_route");
    if (randomRouteItem && specifiedRouteItem) {
        if (route_status === "stopped") {
            // Random-route state: add ✓ to random route
            if (!randomRouteItem.textContent.includes('✓')) {
                randomRouteItem.textContent += ' ✓';
            }
            // Ensure specified route has no ✓
            specifiedRouteItem.textContent = specifiedRouteItem.textContent.replace(' ✓', '');
        } else {
            // Specified-route state: add ✓ to specified route
            if (!specifiedRouteItem.textContent.includes('✓')) {
                specifiedRouteItem.textContent += ' ✓';
            }
            // Ensure random route has no ✓
            randomRouteItem.textContent = randomRouteItem.textContent.replace(' ✓', '');
        }
    }
}

showHistory();
// Define an async function to check and display points
async function checkAndShowPoints() {
    // Check whether person data has been loaded
    if (!persons_loaded_flag) {
        // Define data URL
        const resolvedBaseUrl = (typeof API_BASE_URL !== 'undefined' && API_BASE_URL)
            ? API_BASE_URL
            : ((typeof window !== 'undefined' && window.__AGENT_SERVER__) ? window.__AGENT_SERVER__ : '');
        const normalizedBaseUrl = (resolvedBaseUrl || '').replace(/\/+$/, '');
        const dataUrl = `${normalizedBaseUrl}/api/get_people_list/`;

        try {
            // Load person data
            const data = await loadPersonsData(dataUrl);
            console.log("Person data loaded:", data);

            // Show success toast
            showAlert(`Person data loaded.`);

            // Store loaded data
            const myNationId = (typeof nation_id_me !== 'undefined' && nation_id_me) ? String(nation_id_me).trim() : '';
            if (Array.isArray(data) && myNationId) {
                personsdata = data.filter(person => {
                    const pid = (person && (person.nation_id || person.nationid)) ? String(person.nation_id || person.nationid).trim() : '';
                    return pid !== myNationId;
                });
            } else {
                personsdata = data;
            }

            // Display points
            showpoints();
        } catch (error) {
            console.error("Error loading person data:", error);
            showAlert(`Error loading person data: ${error.message}`);
        }
    }
}

// Delay invoking checkAndShowPoints
setTimeout(checkAndShowPoints, 10000);

function set_shortcut_key() {
    // Attach keyboard event listener to address input
    document.getElementById('home_address').addEventListener('keydown', handleKeyEvent.bind(null, updateHomePosition, closeHomePositionSetting));

    // Attach keyboard event listener to start input
    document.getElementById('start').addEventListener('keydown', handleKeyEvent.bind(null, planRoute, closeRouteSetting));

    // Attach keyboard event listener to end input
    document.getElementById('end').addEventListener('keydown', handleKeyEvent.bind(null, planRoute, closeRouteSetting));
}
// Generic keyboard event handler
function handleKeyEvent(action, closeAction, event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent default form submission
        action(); // Execute corresponding action
    } else if (event.key === 'Escape') {
        event.preventDefault(); // Prevent default behavior
        closeAction(); // Close the corresponding panel
    }
}

// Initialize route display state after page load
//initRouteDisplay();
// Initialize keyboard shortcuts
set_shortcut_key();
// Initialize route planning feature

setTimeout(() => {
  // Check whether mapManager exists and has init method
  if (window.mapManager && typeof window.mapManager.init === 'function') {
    window.mapManager.init();
  } else {
    console.warn('mapManager or its init method is not available. Skipping initialization.');
  }
}, 1000);


// Init
