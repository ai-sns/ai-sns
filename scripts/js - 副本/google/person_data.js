function getPersonDataByNationId(nation_id) {
    if (nation_id == nation_id_me) {
        return person_data_me;
    } else {
        return personsdata.find(person => person.nation_id === nation_id) || null;
    }
}

function getPersonModelByNationId(nation_id) {
    let model = model_loaded_list[nation_id];
    return model;
}

function getPersonPointByNationId(nation_id) {
    let persondata = getPersonDataByNationId(nation_id);
    let location = persondata["location"];
    const point = new google.maps.LatLng(location[1], location[0]);
    return point;
}

function setPersonPointByNationId(nation_id, lng, lat) {
    let persondata = getPersonDataByNationId(nation_id);
    let location = persondata["location"];
    location[0] = lng;
    location[1] = lat;
    persondata["location"] = location;
}

function getPersonModelPointByNationId(nation_id) {
    return getPersonPointByNationId(nation_id);
}

function setPersonModelPointByNationId(nation_id, point) {
    person_model = getPersonModelByNationId(nation_id);
    console.log("the set model point:", point);
    // overlay.setAnchor(coordinates);
    const position = overlay.latLngAltitudeToVector3(point);
    console.log("model.positiona24", person_model.position)
    console.log("model.positionxa24", person_model.position.x)
    console.log("model.positionza24", person_model.position.z)
    console.log("position", position)


    const position2 = overlay.latLngAltitudeToVector3(point, person_model.position);
    console.log("position2", position2)
    console.log("model.position", person_model.position)
    console.log("model.positionx", person_model.position.x)
    console.log("model.positionz", person_model.position.z)


}

function getNationIdByAccount(account) {
    if (account == person_data_me.account) {
        return person_data_me.nation_id;
    } else {
        let persondata = personsdata.find(person => person.account === account) || null;
        return persondata["nation_id"];
    }
}

function getPersonDataByAccount(account) {
    if (account == person_data_me.account) {
        return person_data_me;
    } else {
        return persondata = personsdata.find(person => person.account === account) || null;
    }
}

function getPersonModelByAccount(account) {

    let nation_id = getNationIdByAccount(account);
    let person_model = getPersonModelByNationId(nation_id);
    // 如果没有找到匹配的 account，返回 null
    return person_model;

}

function getPersonPointByAccount(account) {

    let persondata = getPersonDataByAccount(account);
    let location = persondata["location"];
    const point = new google.maps.LatLng(location[1], location[0]);
    return point;

}


