//map conmon map init and load 3d model
var map_type ="google";
var info_window_type = "";
var modelLoadStatus = {
    building: false,
    house: false,
    girl: false,
    boy: false
};
var animationStarted = false;
var is_3d_flag = true;
var init_address = "";
var home_position = null;
var current_position = null;
var plaza_position = null;
var clock = new THREE.Clock();
var mixers = [];
var map;
var marker;
var geocoder;
var directionsService;
var directionsRenderer;
var last_click_point;
var instruct_to_move_flag = false;
var init_route_current_position=null;
var init_route_distance = 0;
var person_data_me;
var model_loaded_list = {};
var nation_id_me = "";
var overlay;
var modelhouse;
var model;
var model2;
var base_url = (typeof window !== 'undefined' && window.__AI_SNS_SERVER__) ? window.__AI_SNS_SERVER__ : "";
var persons_loaded_flag =false;
var personsdata = [];

