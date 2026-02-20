//interact with python

var api_object = null;

document.addEventListener("DOMContentLoaded", function () {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        api_object = channel.objects.message_handler;
        api_object.on_chat_message.connect(show_talk_message);
        api_object.on_command_message.connect(handle_command);
        loadMapSetting();
        loadMoreItems(true);
    });
});

var show_talk_message = function (from, to, msg) {
    console.log(from);
    console.log(to);
    from_point = getPersonPointByAccount(from);
    send_chat_msg(from_point.lng, from_point.lat, msg);
}

var handle_command = function (command, param_1, param_2) {

    if (command == "talk_to_it") {
        if (map_type == "google") {
            let marker = getMarkerByNationId(param_1);
            hiddenMarkers[param_1] = marker;
        } else {
            div = document.getElementById(param_1);
            hiddenPoints[param_1] = div;
        }
        talk_to_it(param_1, param_2)
    } else if (command == "move_to_a_place") {
        if (map_type == "google") {
            setPersonModelPointByNationId(nation_id_me, new google.maps.LatLng(parseFloat(param_2), parseFloat(param_1)));
        } else {
            setPersonModelPointByNationId(nation_id_me, new BMapGL.Point(parseFloat(param_2), parseFloat(param_1)));
        }
        setPersonPointByNationId(nation_id_me, parseFloat(param_1), parseFloat(param_2));
        findHim();
    } else if (command == "show_information") {
        addMessageToBoard(param_1);
    } else if (command == "load_information") {
        appendMessageToBoard(param_1);
    } else if (command == "load_map_setting") {
        handle_map_setting_loaded(param_1);
    } else if (command == "clear_chat_history") {
        clear_chat_history();
    } else if (command == "check_place") {
        let lng = parseFloat(param_2.split('_')[0]);
        let lat = parseFloat(param_2.split('_')[1]);
        check_place(param_1, lng, lat)
    }

}

function loadMapSetting() {
    api_object.load_map_setting();
}

function handle_map_setting_loaded(setting_json) {
    const settings = JSON.parse(setting_json);

    settings.current_position = JSON.parse(settings.current_position);
    settings.home_position = JSON.parse(settings.home_position);
    settings.route_current_position = JSON.parse(settings.route_current_position);

    const {
        avatar3d,
        nationid,
        account,
        nick_name,
        avatar,
        profile,
        current_position,
        home_position,
        route_current_position,
        route
    } = settings;
    nation_id_me = nationid;
    home_position = {
        lng: home_position.lng,
        lat: home_position.lat,
        altitude: home_position.altitude
    };
    init_route_current_position = {
        lng: route_current_position.lng,
        lat: route_current_position.lat
    };
    if (route) {
        init_route_distance = parseFloat(route);
    }

    person_data_me = {
        nation_id: nationid, // 使用国家 ID
        account, // 使用账户
        location: [current_position.lng, current_position.lat], // 位置数组，包含经纬度
        nick_name, // 昵称
        avatar, // 头像 URL
        avatar_3d: avatar3d, // 3D 头像
        profile, // 个人资料
        status: "1" // 状态，假设 "1" 表示在线或活动状态
    };

    loadModel(person_data_me);


}

function update_map_setting(field_name, field_value) {
    api_object.update_map_setting(field_name, field_value);
}

function loadMoreItems(init_flag) {
    if (init_flag) {
        api_object.info_load_more("-1");
    } else {
        api_object.info_load_more(info_window_type);
    }
}



