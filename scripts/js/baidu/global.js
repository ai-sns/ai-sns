//map conmon map init and load 3d model
var map_type ="baidu";
var info_window_type = "";
//todo
var modelLoadStatus = {
    building: false,
    house: false,
    girl: false,
    boy: false
};
var animationStarted = false;
var is_3d_flag = true;
var instruct_to_move_flag = false;
var marker = null;
var init_position_flag = false;
var map = new BMapGL.Map('map');
var geoc = new BMapGL.Geocoder();
var last_click_point;
var driving;
var gpsPositions = [];
var currentRoute;
var current_track_point;
var trackAni;
var init_address = "";
var home_position = null;
var current_position = null;
var init_route_current_position=null;
var plaza_position = null;
var person_data_me;
var nation_id_me = "";
var base_url = "http://www.ai-sns.org";
var persons_loaded_flag =false;
var personsdata = [];
var model_loaded_list = {};
