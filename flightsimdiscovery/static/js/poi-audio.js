//html config

let allVoices, allLanguages, primaryLanguages, langtags, langhash, langcodehash;
let txtFld, playBtn, pauseBtn, resumeBtn, stopBtn, replayBtn, next, Btn, settingsBtn, speakerMenu, languageMenu, blurbs;
let currentPoiQuerySelect;
let voiceIndex = 0;
let initialSetup = true;


speech = new SpeechSynthesisUtterance();
let updatePAIntervalID;
var myTimeout;
const SEARCH_RADIUS = 9300;   //meters

//play list details
let selectMenuPlayList;
let poisWithinArea;
let current_poi_playing;
let pois_played;

//main entry 
function pa_init() {

    configureHTML();

    //re-set play/pause button value
    $('#pa_play_pause').val('play');
    $('#pa_play_pause_icon').removeClass('fa-pause');
    $('#pa_play_pause_icon').addClass('fa-play');
    $('#pa_replay_btn').val('play');

    //update play list every 10 seconds
    updatePAIntervalID = setInterval(() => {
        pa_update_play_list();
    }, 5000);

}

function configureHTML() {

    // speech = new SpeechSynthesisUtterance();
    updatePAIntervalID = null;
    myTimeout = null;

    //play list details
    selectMenuPlayList = null;
    poisWithinArea = null;
    current_poi_playing = null;
    pois_played = [];

    playBtn = qs("#pa_play_pause");
    playBtn.addEventListener("click", paPlayPause, false);

    replayBtn = qs("#pa_replay_btn");
    replayBtn.addEventListener("click", paReplay, false);
    nextBtn = qs("#pa_next_btn");
    nextBtn.addEventListener("click", paNext, false);

    stopBtn = qs("#pa_stop");
    stopBtn.addEventListener("click", paStop, false);
    settingsBtn = qs("#pa_settings");
    settingsBtn.addEventListener("click", paSettings, false);
    currentPoiQuerySelect = qs("#select_poi_play");

    populateSelectMenu([]);

    // currentPoiQuerySelect.addEventListener("change", selectPOI, false);
    $('#select_poi_play').on("change", playPOIFromSelectMenu);

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
        }
        setUpVoices(); //for all the other browsers
    } else {
        playBtn.disabled = true;
        speakerMenu.disabled = true;
        languageMenu.disabled = true;
        pa_disconnect();
        console.log('no uspeech synthesis on this browser - disconnecting');
        $("#warning").attr("hidden", false);
        $('#active_flight_flash_text').text("Your browser doesn't support windows speech synthesis");
    }


}


speech.onend = function (event) {

    $('#pa_play_pause').val('play');
    $('#pa_play_pause_icon').addClass('fas fa-play');
    $('#pa_play_pause_icon').removeClass('fa-pause fa-resume');

    if (current_poi_playing) {
        pois_played.push(current_poi_playing['id']);
    }
    clearTimeout(myTimeout);

    current_poi_playing = null;
}


function pa_update_play_list() {

    //only update play list if play poi if not currently playing
    if (current_poi_playing != null) {

        return;
    }

    let af_details_dict = getAFDetails();
    let last_update_ms = af_details['last_update_ms'];
    current_date_ms = Date.now();
    diff_millis = current_date_ms - last_update_ms;

    /*  UNCOMMENT OUT THESE WHEN NOT TESTING */
    if (diff_millis > 20000) {
        console.log('no update for 20 seconds - disconnecting');
        pa_disconnect();
        return;
    }

    current_lat = af_details_dict['user_lat'];
    current_lng = af_details_dict['user_lng'];

    //TESTING ONLY - SEE ABOVE
    // current_lat = 51.508407;
    // current_lng = -0.101282;
    // current_lat = -23.529724;
    // current_lng = -69.609087;

    //find POIs within 5nm and update play list
    poisWithinArea = getPoisWithinArea(new google.maps.LatLng(current_lat, current_lng));

    populateSelectMenu(poisWithinArea);

    if (selectMenuPlayList.length > 0) {

        // //cancel before playing to stop bug in chrome sometimes wont play
        // window.speechSynthesis.cancel();
        paPlayPause();
    }
}

//PLAY - PAUSE - RESUME FUNCTIONALITY
function paPlayPause() {
    btn_val = $('#pa_play_pause').val();

    if (btn_val == 'play') {

        //check to see if user had previsouly stopped.  if so we need to re-initialise the timeout
        if (updatePAIntervalID == null) {

            pa_init();
            return;
        }

        poi_to_play = getSelectedPoi();
        if (poi_to_play) {
            paPlayAudio(poi_to_play);
        } else {
            return;
        }


        //change select statement text by appending 'Playing'
        $("#select_poi_play option:selected").text('Playing: ' + current_poi_playing_name);
        $('#pa_play_pause').val('pause');
        $('#pa_play_pause_icon').toggleClass('fa-play fa-pause');

    } else if (btn_val == 'pause') {

        clearTimeout(myTimeout);
        $('#pa_play_pause').val('resume');
        $('#pa_play_pause_icon').toggleClass('fa-pause fa-play');
        window.speechSynthesis.pause();
        $("#select_poi_play option:selected").text('Paused: ' + current_poi_playing_name);

    } else if (btn_val == 'resume') {

        $('#pa_play_pause').val('pause');
        $('#pa_play_pause_icon').toggleClass('fa-pause fa-play');
        window.speechSynthesis.resume();
        myTimeout = setTimeout(myTimer, 10000);
        $("#select_poi_play option:selected").text('Playing: ' + current_poi_playing_name);
    }
}

function paPlayAudio(poi_to_play) {

    let sval = Number(speakerMenu.value);
    speech.voice = allVoices[sval];
    speech.lang = speech.voice.lang;
    speech.rate = 0.9;
    current_poi_playing = poi_to_play;
    current_poi_playing_id = current_poi_playing['id'];
    current_poi_playing_name = current_poi_playing['name'];
    textTo_play = current_poi_playing_name + '\n' + current_poi_playing['description'];
    txtFld.value = textTo_play;
    speech.text = textTo_play;

    //cancel solves strange bugs
    window.speechSynthesis.cancel();

    //timer needed as chrome will stop playing text after about 15s
    myTimeout = setTimeout(myTimer, 10000);
    window.speechSynthesis.speak(speech);
}

function paStop() {

    //user may hit stop button af
    if (current_poi_playing) {
        pois_played.push(current_poi_playing['id']);
    }

    clearTimeout(myTimeout);
    clearInterval(updatePAIntervalID);
    current_poi_playing = null;

    // populateSelectMenu(poisWithinArea);
    window.speechSynthesis.cancel();
    $('#select_poi_play').prop('disabled', 'disabled');
    $('#select_poi_play').append(`<option selected value="all" selected>Press 'Play' to resume</option>`);
    $("#pa_audio_toolbar").prop('hidden', true);

    updatePAIntervalID = null;
    pois_played = [];
    console.log("stopping POI audio")
}

function paNext() {

    nextPOISelectIndex = null;

    // only play next if currently playing a poi and there is more than one poi to play in select lilst
    if ((!current_poi_playing) || (selectMenuPlayList.length < 2)) {
        console.log('NO NEXT POI TO PLAY.  Playing current one')
        nextPOISelectIndex = 0;

    }

    current_poi_playing_id = current_poi_playing['id'];

    try {

        //lets find that poi in the select list and play the next one
        for (const [index, selectMenuPlayPOI] of selectMenuPlayList.entries()) {
            if (selectMenuPlayPOI['id'] == current_poi_playing_id) {
                nextPOISelectIndex = index + 1;
                break;
            }
        }

        //Remove current poi playing 'playing' text 
        $('#select_poi_play option[value="' + current_poi_playing_id + '"]').text(current_poi_playing['name']);

        //clear the current timeout
        clearTimeout(myTimeout);
        console.log('PLAYING NEXT POI')

        //play next poit in list
        $("#select_poi_play option:selected").text('Playing: ' + selectMenuPlayList[nextPOISelectIndex]['name']);
        $("#select_poi_play option:selected").val(selectMenuPlayList[nextPOISelectIndex]['id']);
        $('#pa_play_pause').val('pause');
        $('#pa_play_pause_icon').removeClass('fa-play');
        $('#pa_play_pause_icon').addClass('fa-pause');
        nextPOItoPlay = selectMenuPlayList[nextPOISelectIndex];
        paPlayAudio(nextPOItoPlay);

    }
    catch (err) {
        console.log('no next poi in play list...should really disable the next button');
        console.log(err);
    }
}

function paReplay() {

    var poi_to_play = current_poi_playing;

    //rewind to previous played poi
    if (current_poi_playing == null) {
        if (pois_played.length > 0) {
            poi_to_play_id = pois_played.slice(-1)[0];
            for (let i = 0; i < pois_array.length; i++) {
                if (pois_array[i]['id'] == poi_to_play_id) {
                    poi_to_play = pois_array[i];
                    select_text = "Playing: " + poi_to_play['name'];
                    // $('#select_poi_play').prepend('<option selected value="'+poi_to_play_id+'">'+select_text+'</option>');
                    $("#select_poi_play option:selected").text('Playing: ' + poi_to_play['name']);
                    break;
                }
            }

        } else {
            console.log("no poi played so cant rewind.  should disable the button")
            return;
        }
    } else {
        //rewind to beginning of the current poi playing
        console.log('REPLAYING CURRENT POI')
        $("#select_poi_play option:selected").text('Playing: ' + poi_to_play['name']);
    }

    //clear the current timeout
    clearTimeout(myTimeout);
    paPlayAudio(poi_to_play);

    $('#pa_play_pause').val('pause');
    $('#pa_play_pause_icon').removeClass('fa-play');
    $('#pa_play_pause_icon').addClass('fa-pause');

}

function playPOIFromSelectMenu() {
    console.log('playing poi from select menu');

    //we need to remove current poi playing 'playing' text 
    if (current_poi_playing) {
        $('#select_poi_play option[value="' + current_poi_playing['id'] + '"]').text(current_poi_playing['name']);
    }

    poi_id = $(select_poi_play).find(":selected").val();
    poiToPlay = getSelectedPoi(poi_id);
    $("#select_poi_play option:selected").text('Playing: ' + poiToPlay['name']);
    $('#pa_play_pause').val('pause');
    $('#pa_play_pause_icon').toggleClass('fa-play fa-pause');
    paPlayAudio(poiToPlay);
}

function pa_disconnect() {
    console.log("disconnecting from poi audio");
    paStop();
    // clearInterval(updatePAIntervalID);
}

function paSettings() {

    is_visible = $('#pa_audio_toolbar').is(":visible");
    if (is_visible) {
        $("#pa_audio_toolbar").prop('hidden', true);
    } else {
        $("#pa_audio_toolbar").removeProp('hidden');
    }
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

function populateSelectMenu(poisWithinArea) {

    var tempPoiPlayList = [];
    var html = ``;
    var enableAllButtons = true;

    //disable select menu by default
    $('#select_poi_play').prop('disabled', 'disabled');


    //do not update select statement until play has finished.
    if (current_poi_playing) {
        return;
    }

    //add to play list if nearby pois are found
    if (poisWithinArea.length > 0) {

        $('#select_poi_play').prop('disabled', false);
        poisWithinArea.forEach(function (poi, i) {

            //only add to list if POI has NOT been played previously
            if (!pois_played.includes(poi['id'])) {
                html += `<option value=${poi['id']}>${poi['name']}</option>`;
                tempPoiPlayList.push(poi);
            }
            // console.log('poi already played: ' + poi['id']);
            // if (poisWithinArea.length == 1) {
            //     $('#select_poi_play').prop('disabled', 'disabled');
            // html = `<option selected value="all" selected>Searching for POI's within 10km ...</option>`;
            // return;
            // enableAllButtons = false;
            // }              

        });
    } else {
        $('#select_poi_play').prop('disabled', 'disabled');
        // html = `<option selected value="all" selected>Searching for POI's within 10km ...</option>`;
        enableAllButtons = false;
    }

    //Allow user to select from list as there is at least one option
    if (tempPoiPlayList.length > 0) {
        $("input").prop('disabled', false);
    } else {
        $('#select_poi_play').prop('disabled', 'disabled');
        html = `<option selected value="all" selected>Searching for POI's within 10km ...</option>`;
    }

    // document.getElementById('select_poi_play').innerHTML = html;
    $('#select_poi_play').html(html);

    //disable buttons if searching for pois
    changeBtnState(enableAllButtons);

    //update select menu play list which is used by replay and next functions
    selectMenuPlayList = tempPoiPlayList;
}

function getNearbyPOIs() {

    console.log('get pois');
}

function createLanguageMenu() {
    let code = `<option selected value="all">Show All</option>`;
    let langnames = [];
    primaryLanguages.forEach(function (lobj, i) {

        two_letter_lng_code = lobj.substring(0, 2);
        full_name_lng_dict = langcodehash[two_letter_lng_code];

        //continue if code isnt in the langcodehash
        if (full_name_lng_dict == null) {
            return true;
        }
        full_name_lng = full_name_lng_dict['name'];
        // langnames.push(langcodehash[lobj.substring(0, 2)].name);
        langnames.push(full_name_lng);
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

function getPoisWithinArea(current_position) {

    //test
    var closestMarker = -1;
    var closestPOI = '';
    var closestDistance = Number.MAX_VALUE;

    pois_within_search = [];
    pois_array = pois_array;
    pois_array.forEach(function (poi, i) {

        poi_lat = parseFloat(poi['lat']);
        poi_lng = parseFloat(poi['lng']);


        var distance = google.maps.geometry.spherical.computeDistanceBetween(new google.maps.LatLng(poi_lat, poi_lng), current_position);

        //test
        if (distance < closestDistance) {
            closestMarker = i;
            closestDistance = distance;
            closestPOI = poi['name'];
        }

        if (distance < SEARCH_RADIUS) {
            poi_dict = {};
            poi_dict['id'] = poi['id'];
            poi_dict['name'] = poi['name'];
            poi_dict['description'] = poi['description'];
            poi_dict['distance_from_current_position'] = distance;
            pois_within_search.push(poi_dict)
        }
    });

    console.log('Nearest POI is ' + closestPOI + ' (' + (closestDistance / 1000).toFixed(1) + 'km)');

    sorted_play_list = pois_within_search.sort(sortPlaylist);

    return sorted_play_list
    // return pois_within_search;

}

function getSelectedPoi() {

    selectValue = document.getElementById('select_poi_play').value;
    poi_to_play = null;

    for (let poi of selectMenuPlayList) {
        if (poi['id'] == selectValue) {
            poi_to_play = poi;
            break;
        }
    }

    return poi_to_play;
}

function sortPlaylist(a, b) {
    if (a.distance_from_current_position < b.distance_from_current_position) {
        return -1;
    }
    if (a.distance_from_current_position > b.distance_from_current_position) {
        return 1;
    }
    return 0;
}

function changeBtnState(toEnable) {

    if (toEnable) {
        $('#pa_replay_btn').removeAttr('disabled');
        $('#pa_play_pause').removeAttr('disabled');
        $('#pa_stop').removeAttr('disabled');
        $('#pa_next_btn').removeAttr('disabled');
    } else {
        $("#pa_replay_btn").attr('disabled', 'disabled');
        $("#pa_play_pause").attr('disabled', 'disabled');
        $("#pa_stop").attr('disabled', 'disabled');
        $("#pa_next_btn").attr('disabled', 'disabled');

    }
}

function myTimer() {
    window.speechSynthesis.pause();
    window.speechSynthesis.resume();
    myTimeout = setTimeout(myTimer, 10000);
}
