let speech = new SpeechSynthesisUtterance();
let defaultBlurb = "The Amazon River in South America is the largest river by discharge volume of water in the world, and the disputed longest river in the world.";
let allVoices, allLanguages, primaryLanguages, langtags, langhash, langcodehash;
let txtFld, playBtn, pauseBtn, resumeBtn, stopBtn, speakerMenu, languageMenu, blurbs;
let currentPoiSelect;
let voiceIndex = 0;
let initialSetup = true;

let updatePAIntervalID = null;
const SEARCH_RADIUS = 5000;   //meters

//html config
playBtn = qs("#pa_play_pause");
playBtn.addEventListener("click", paPlayPause, false);
stopBtn = qs("#pa_stop");
stopBtn.addEventListener("click", paStop, false);
currentPoiSelect = qs("#select_poi_play");

// setUpNearbyPOIsSelect([]);
// currentPoiSelect.addEventListener("change", selectPOI, false);
$('#select_poi_play').on( "change", selectPOI );

txtFld = qs("#textFld");
speakerMenu = qs("#speakerMenu");
langtags = getLanguageTags();

speakerMenu.addEventListener("change", selectSpeaker, false);

// rateFld = qs("#rateFld");
languageMenu = qs("#languageMenu");
languageMenu.addEventListener("change", selectLanguage, false);
langhash = getLookupTable(langtags, "name");
langcodehash = getLookupTable(langtags, "code");

if (window.speechSynthesis) {
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
        //Chrome gets the voices asynchronously so this is needed
        window.speechSynthesis.onvoiceschanged = setUpVoices;
        $("#warning").attr("hidden",true);
    }
    setUpVoices(); //for all the other browsers
} else {
    playBtn.disabled = true;
    speakerMenu.disabled = true;
    languageMenu.disabled = true;
    $("#warning").attr("hidden",false);
}

speech.onend = function(event) {
    
    $('#pa_play_pause').val('play');
    $('#pa_play_pause_icon').addClass('fas fa-play');
    $('#pa_play_pause_icon').removeClass('fa-pause fa-resume');
}

//main entry 
function pa_init(){


    updatePAIntervalID =setInterval(() => {
        pa_update_play_list() 
    }, 8000 );

}

function pa_update_play_list(){

    let af_details_dict = getAFDetails();
    // current_lat = af_details_dict['user_lat'];
    // current_lng = af_details_dict['user_lng'];
    current_lat = 51.508407;
    current_lng = -0.101282;

    //find POIs within 5nm and update play list
    play_list = getPoisToPlay(new google.maps.LatLng(current_lat, current_lng));
    setUpNearbyPOIsSelect(play_list);
}

function pa_diosconnect(){
    console.log("discommectopm frp, poi audio");
    clearInterval(updatePAIntervalID);

}


function setUpVoices() {
    allVoices = getAllVoices();
    allLanguages = getAllLanguages(allVoices);
    primaryLanguages = getPrimaryLanguages(allLanguages);
    filterVoices();
    if (initialSetup && allVoices.length) {
        initialSetup = false;
        createLanguageMenu();
        $('#languageMenu').val('en').trigger('click');
        filterVoices();
   
    }
}
function paPlayPause() {
    btn_val = $('#pa_play_pause').val();

    if (btn_val == 'play') {
        let sval = Number(speakerMenu.value);
        speech.voice = allVoices[sval];
        speech.lang = speech.voice.lang;
        console.log(speech.lang);
        speech.text = txtFld.value;
        window.speechSynthesis.speak(speech);
        $('#pa_play_pause').val('pause');
        $('#pa_play_pause_icon').toggleClass('fa-play fa-pause');

    } else if (btn_val == 'pause') {

        $('#pa_play_pause').val('resume');
        $('#pa_play_pause_icon').toggleClass('fa-pause fa-play');
        window.speechSynthesis.pause();
    } else if (btn_val == 'resume') {

        $('#pa_play_pause').val('pause');
        $('#pa_play_pause_icon').toggleClass('fa-pause fa-play');
        window.speechSynthesis.resume();
    } 
}

// function pa_pause()  {
//     window.speechSynthesis.pause();
// }

// function pa_resume()  {
//     window.speechSynthesis.resume();
// }

function paStop()  {

    window.speechSynthesis.cancel();
}

function setUpNearbyPOIsSelect(play_list) {


    let html = ``;

    //add to play list if nearby pois are found
    if(play_list.length > 0) {

        play_list.forEach(function (poi, i) {
            poi_id = poi['id'];
            poi_name = poi['name'];
            html += `<option value=${poi_id}>${poi_name}</option>`;
            html += `</option>`;
        });
    } else {
        html = `<option selected value="all" selected>No POIs within 5nm</option>`;
    }
    
    document.getElementById('select_poi_play').innerHTML = html;
}

function getNearbyPOIs() {

    console.log('get pois');
}

function selectPOI() {
    console.log('select poi')
}

function createLanguageMenu() {
    let code = `<option selected value="all">Show All</option>`;
    let langnames = [];
    primaryLanguages.forEach(function (lobj, i) {
        langnames.push(langcodehash[lobj.substring(0, 2)].name);
    });
    langnames.sort();
    langnames.forEach(function (lname, i) {
        let lcode = langhash[lname].code;
        code += `<option value=${lcode}>${lname}</option>`;
    });
    languageMenu.innerHTML = code;
}
function createSpeakerMenu(voices) {
    let code = ``;
    voices.forEach(function (vobj, i) {
        code += `<option value=${vobj.id}>${vobj.name} (${vobj.lang})`;
        code += vobj.voiceURI.includes(".premium") ? ' (premium)' : ``;
        code += `</option>`;
    });
    speakerMenu.innerHTML = code;
}
function getAllLanguages(voices) {
    let langs = [];
    voices.forEach(vobj => {
        langs.push(vobj.lang.trim());
    });
    return [...new Set(langs)];
}
function getPrimaryLanguages(langlist) {
    let langs = [];
    langlist.forEach(vobj => {
        langs.push(vobj.substring(0, 2));
    });
    return [...new Set(langs)];
}
function selectSpeaker() {
    voiceIndex = speakerMenu.selectedIndex;
}
function selectLanguage() {
    filterVoices();
    speakerMenu.selectedIndex = 0;
}
function filterVoices() {
    let langcode = languageMenu.value;
    voices = allVoices.filter(function (voice) {
        return langcode === "all" ? true : voice.lang.indexOf(langcode + "-") >= 0;
    });
    createSpeakerMenu(voices);
    txtFld.value = defaultBlurb;
    speakerMenu.selectedIndex = voiceIndex;
}


function getAllVoices() {
    let voicesall = window.speechSynthesis.getVoices();
    let vuris = [];
    let voices = [];

    //unfortunately we have to check for duplicates
    voicesall.forEach(function (obj, index) {
        let uri = obj.voiceURI;
        if (!vuris.includes(uri)) {
            vuris.push(uri);
            voices.push(obj);
        }
    });
    voices.forEach(function (obj, index) { obj.id = index; });
    return voices;
}

function getLanguageTags() {
    let langs = ["ar-Arabic", "cs-Czech", "da-Danish", "de-German", "el-Greek", "en-English", "eo-Esperanto", "es-Spanish", "et-Estonian", "fi-Finnish", "fr-French", "he-Hebrew", "hi-Hindi", "hu-Hungarian", "id-Indonesian", "it-Italian", "ja-Japanese", "ko-Korean", "la-Latin", "lt-Lithuanian", "lv-Latvian", "nb-Norwegian Bokmal", "nl-Dutch", "nn-Norwegian Nynorsk", "no-Norwegian", "pl-Polish", "pt-Portuguese", "ro-Romanian", "ru-Russian", "sk-Slovak", "sl-Slovenian", "sq-Albanian", "sr-Serbian", "sv-Swedish", "th-Thai", "tr-Turkish", "zh-Chinese"];
    let langobjects = [];
    for (let i = 0; i < langs.length; i++) {
        let langparts = langs[i].split("-");
        langobjects.push({ "code": langparts[0], "name": langparts[1] });
    }
    return langobjects;
}
// Generic Utility Functions
function qs(selectorText) {
    
    return document.querySelector(selectorText);
}
function getLookupTable(objectsArray, propname) {
    return objectsArray.reduce((accumulator, currentValue) => (accumulator[currentValue[propname]] = currentValue, accumulator), {});
}

function getPoisToPlay(current_position) {

    //test
    var closestMarker = -1;
    var closestPOI = '';
    var closestDistance = Number.MAX_VALUE;

    pois_within_search = [];
    pois_array = pois_array;
    pois_array.forEach(function (poi, i) {

        poi_lat =parseFloat(poi['lat']);
        poi_lng =parseFloat(poi['lng']);


        var distance = google.maps.geometry.spherical.computeDistanceBetween(new google.maps.LatLng(poi_lat, poi_lng), current_position );
        
        //test
        if ( distance < closestDistance ) {
            closestMarker = i;
            closestDistance = distance;
            closestPOI = poi['name'];
        }
        
        if ( distance < SEARCH_RADIUS ) {
            poi_dict = {};
            poi_dict['id'] = poi['id'];
            poi_dict['name'] = poi['name'];
            poi_dict['description'] = poi['description'];
            poi_dict['distance_from_current_position'] = distance;
            pois_within_search.push(poi_dict)
        }
    });

    console.log(closestDistance);
    console.log(closestPOI);

    sorted_play_list = pois_within_search.sort( sortPlaylist );
    return sorted_play_list
    // return pois_within_search;
 
}

function sortPlaylist( a, b ) {
    if ( a.distance_from_current_position < b.distance_from_current_position ){
      return -1;
    }
    if ( a.distance_from_current_position > b.distance_from_current_position ){
      return 1;
    }
    return 0;
}
  

