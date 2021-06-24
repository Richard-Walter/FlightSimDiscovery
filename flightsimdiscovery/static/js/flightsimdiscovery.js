/**
 * FLight Sim Discovery Javascript file
 * ScrollIt.js(scroll•it•dot•js) makes it easy to make long, vertically scrolling pages.
 *
 */


var region_country = {
  "Asia - Southern": [
    "Afghanistan",
    "Bangladesh",
    "Bhutan",
    "India",
    "Iran",
    "Maldives",
    "Nepal",
    "Pakistan",
    "Sri Lanka",
  ],
  "Europe - Southern": [
    "Albania",
    "Andorra",
    "Bosnia and Herzegovina",
    "Croatia",
    "Gibraltar",
    "Greece",
    "Italy",
    "Kosovo",
    "Malta",
    "Montenegro",
    "North Macedonia",
    "Portugal",
    "San Marino",
    "Serbia",
    "Slovenia",
    "Spain",
  ],
  "Africa - Northern": [
    "Algeria",
    "Egypt",
    "Libya",
    "Morocco",
    "Sudan",
    "Tunisia",
    "Western Sahara",
  ],
  Oceania: [
    "American Samoa",
    "Australia",
    "Christmas Island",
    "Cocos (Keeling) Islands",
    "Cook Islands",
    "Fiji",
    "French Polynesia",
    "Federated States of Micronesia",
    "Guam",
    "Kiribati",
    "Marshall Islands",
    "Nauru",
    "New Caledonia",
    "New Zealand",
    "Niue",
    "Norfolk Island",
    "Northern Mariana Islands",
    "Oceania (Federated States of)",
    "Palau",
    "Papua New Guinea",
    "Pitcairn",
    "Samoa",
    "Solomon Islands",
    "Tokelau",
    "Tonga",
    "Tuvalu",
    "Vanuatu",
    "Wallis and Futuna",
  ],
  "Africa - Middle": [
    "Angola",
    "Cameroon",
    "Central African Republic",
    "Chad",
    "Congo",
    "Congo, Democratic Republic of the",
    "Equatorial Guinea",
    "Gabon",
    "Sao Tome and Principe",
  ],
  Caribbean: [
    "Anguilla",
    "Antigua and Barbuda",
    "Aruba",
    "Bahamas",
    "Barbados",
    "British Virgin Islands",
    "Cayman Islands",
    "Cuba",
    "Dominica",
    "Dominican Republic",
    "Grenada",
    "Guadeloupe",
    "Heard Island and McDonald Islands",
    "Jamaica",
    "Martinique",
    "Montserrat",
    "Puerto Rico",
    "Saint Barthélemy",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Vincent and the Grenadines",
    "Trinidad and Tobago",
    "Turks and Caicos Islands",
    "U.S. Virgin Islands",
  ],
  Antartica: ["Antarctica"],
  "America - South": [
    "Argentina",
    "Bolivia",
    "Brazil",
    "Chile",
    "Colombia",
    "Ecuador",
    "Falkland Islands (Malvinas)",
    "French Guiana",
    "Haiti",
    "Paraguay",
    "Peru",
    "South Georgia",
    "Suriname",
    "Uruguay",
    "Venezuela",
  ],
  "Middle East": [
    "Armenia",
    "Azerbaijan",
    "Bahrain",
    "Cyprus",
    "Georgia",
    "Iraq",
    "Israel",
    "Jordan",
    "Kuwait",
    "Lebanon",
    "Oman",
    "Palestine, State of",
    "Qatar",
    "Saudi Arabia",
    "Syria",
    "Turkey",
    "United Arab Emirates",
    "Yemen",
  ],
  "Europe - Western": [
    "Austria",
    "Belgium",
    "France",
    "Germany",
    "Liechtenstein",
    "Luxembourg",
    "Monaco",
    "Netherlands",
    "Switzerland",
  ],
  "Europe - Eastern": [
    "Belarus",
    "Bulgaria",
    "Czechia",
    "Hungary",
    "Moldova, Republic of",
    "Poland",
    "Romania",
    "Russian Federation",
    "Slovakia",
    "Ukraine",
  ],
  "America - Central": [
    "Belize",
    "Costa Rica",
    "El Salvador",
    "Guatemala",
    "Guernsey",
    "Honduras",
    "Mexico",
    "Nicaragua",
    "Panama",
  ],
  "Africa - Western": [
    "Benin",
    "Burkina Faso",
    "Cabo Verde",
    "Côte d'Ivoire",
    "Gambia",
    "Ghana",
    "Guinea",
    "Guinea-Bissau",
    "Guyana",
    "Liberia",
    "Mali",
    "Mauritania",
    "Niger",
    "Nigeria",
    "Saint Helena",
    "Senegal",
    "Sierra Leone",
    "Togo",
  ],
  "America - Northern": [
    "Bermuda",
    "Canada",
    "Greenland",
    "Saint Pierre and Miquelon",
    "United States of America",
  ],
  "Africa - Southern": [
    "Botswana",
    "Eswatini",
    "Lesotho",
    "Namibia",
    "South Africa",
    "Swaziland",
    "Zambia",
    "Zimbabwe",
  ],
  "Africa - Eastern": [
    "British Indian Ocean Territory",
    "Burundi",
    "Comoros",
    "Djibouti",
    "Eritrea",
    "Ethiopia",
    "French Southern Territories",
    "Kenya",
    "Madagascar",
    "Malawi",
    "Mauritius",
    "Mayotte",
    "Mozambique",
    "Réunion",
    "Rwanda",
    "Seychelles",
    "Somalia",
    "South Sudan",
    "Tanzania",
    "Uganda",
  ],
  "Asia - South-eastern": [
    "Brunei",
    "Cambodia",
    "Indonesia",
    "Laos",
    "Malaysia",
    "Myanmar",
    "Philippines",
    "Singapore",
    "Thailand",
    "Timor-Leste",
    "VietNam",
  ],
  "Asia - Eastern": [
    "China",
    "Hong Kong",
    "Japan",
    "Macao",
    "Mongolia",
    "North Korea",
    "South Korea",
    "Taiwan",
  ],
  "Europe - Northern": [
    "Denmark",
    "Estonia",
    "Faroe Islands",
    "Finland",
    "Great Britain",
    "Iceland",
    "Ireland",
    "Isle of Man",
    "Jersey",
    "Latvia",
    "Lithuania",
    "Norway",
    "Svalbard and Jan Mayen",
    "Sweden",
  ],
  "Asia - Central": [
    "Kazakhstan",
    "Kyrgyzstan",
    "Tajikistan",
    "Turkmenistan",
    "Uzbekistan",
  ],
};

var countryList = getCountryList();
var country_default = $('#countryDefaultVaule').val();
// console.log(country_default)

//add change listener on region dropdown to dynamically update country
$("#selectRegion")
  .change(function () {

    if (this.value.trim() != 'Region') {
      $('#selectCountry').empty();
      // country_default = "Country"
      $('#selectCountry').html('<option data-display="Country">Country</option>');
      // get the second dropdown
      $("#selectCountry").append(
        // get array by the selected value
        region_country[this.value.trim()]
          // iterate  and generate options
          .map(function (v) {
            // generate options with the array element
            return $("<option/>", {
              value: v,
              text: v,
            });
          })
      );
      // $('#selectCountry').val(country_default);
    } else {

      $('#selectCountry').empty();
      $('#selectCountry').html('<option data-display="Country">Country</option>');
      $.each(countryList, function (i, p) {
        $('#selectCountry').append($('<option></option>').val(p).html(p));
      });

      // set default value
      $('#selectCountry').val("Country");

    }

  })

// set default value
$('#selectCountry').val(country_default);

function getCountryList() {

  countryList = [];
  // for (var i = 0; i < region_country.length; i++) {
  for (const [region, regions_countries] of Object.entries(region_country)) {
    // var regions_countries = value;
    // console.log(regions_countries);
    Array.prototype.push.apply(countryList, regions_countries);
    countryList.sort();
  }
  // console.log(countryList);
  return countryList;
}

function getDefaultAirportIWDeatils(airport_IW_details) {


  let tower_freq = parseFloat(airport_IW_details['Tower_Freq']);
  let atis_freq = parseFloat(airport_IW_details['ATIS_Freq']);
  let awos_freq = parseFloat(airport_IW_details['AWOS_Freq']);
  let asos_freq = parseFloat(airport_IW_details['ASOS_Freq']);
  let unicom_freq = parseFloat(airport_IW_details['UNICOM_Freq']);

  var airport_comms_html = "";

  if(atis_freq > 0) {
    
    airport_comms_html += '<p class="ml-2">ATIS: ' + insertDecimal(atis_freq) + '</p>';
  }
  if(tower_freq >0) {
    airport_comms_html += '<p class="ml-2">TWR: ' + insertDecimal(tower_freq) + '</p>';
  }
  if(awos_freq > 0) {
    airport_comms_html += '<p class="ml-2">AWOS: ' + insertDecimal(awos_freq) + '</p>';
  }
  if(asos_freq > 0) {
    airport_comms_html += '<p class="ml-2">ASOS: ' + insertDecimal(asos_freq) + '</p>';
  }
  if(unicom_freq > 0) {
    airport_comms_html += '<p class="ml-2">UNICOM: ' + insertDecimal(unicom_freq) + '</p>';
  }

  //if no airport comms found
  if (airport_comms_html) {
    
    airport_comms_html = '<div id="defaultAirportIWInfo" class="my-1 p-1 border border-seconday iw_copy_latlng" style="text-align: left">' + airport_comms_html;
    
  } else {
    airport_comms_html = '<div class="" style="text-align: left">' + airport_comms_html +'</div>';
  }

  return airport_comms_html;
}

function getIWIconsHTML(latitude, longitude, marker_name, country, cateogry, nearest_icao) {

  
  var skyvectory_hmtl = ''

  if ((cateogry.includes('Airport'))&&(nearest_icao))  {
    skyvectory_hmtl = '<a href="https://skyvector.com/airport/' + nearest_icao + '" target="_blank" class="fa fai fai-plane fa-plane" title="Skyvector"></a>'
  }

  iw_icons_html = 
  '<div class="my-1 border border-seconday ">' +

  '<a href="https://www.google.com/search?q=' + marker_name + ', ' + country + '" target="_blank" class="fa fai  fa-google" title="Google"></a>'+
  '<a href="https://en.wikipedia.org/wiki/' + marker_name + '" target="_blank" class="fa fai  fa-wikipedia-w" title="Wikipedia"></a>'+
  '<a href="https://www.youtube.com/results?search_query=' + marker_name + ', ' + country + '" target="_blank" class="fa fai fa-youtube" title="Youtube"></a>'+
  skyvectory_hmtl+
  // '<a href="#" class="fa fai fai-plane fa-plane" title="Google"></a>'+
  '<i href="" id="copy_coords_icon" class="fa fai fa-map-marker-alt" title="Copy coordinates" onclick="copy_latLon()" style="cursor:pointer"></i>'+
  '<p id="coords_copied_txt" class="my-0" style="font-size: 0.8em; display:none" >Coorindates copied: ' + latitude + ', ' + longitude + '</p>' +
  // '<p class="iw_latlng"><i class="mx-2 fas fa-map-marker-alt" style="color:#993426;"></i>  ' + latitude + ', ' + longitude + ' <button id="copylatlong"  class="btn btn-outline-secondary btn-sm mx-2 py-0" style="font-size: 0.8em;" onclick="copy_latLon()">Copy</button> ' + '</p>' +
  '<input type="hidden" id="poi_lat_long" name="poi_lat_long" value="' + latitude + ', ' + longitude + '">' +
  '</div>'

  return iw_icons_html
}

function insertDecimal(num) {
  return (num / 1000).toFixed(3);
}

//SHOW USER FLIGHT ON MAP
var user_id = getUserID()
var map = getMap()
var marker = 

//create inital user marker info
userMarkerInfo = {

  id: user_id,
  map: map,
  marker: null,
}

var ajaxUserMarkerObj = { //Object to save cluttering the namespace.

  options: {
      type: 'POST',
      url: "/users/get_user_location", //The resource that delivers loc data.
      dataType: "text", //The type of data tp be returned by the server.
      data: {user_id: user_id},
  },

  delay: 5000, //(milliseconds) the interval between successive gets.
  errorCount: 0, //running total of ajax errors.
  errorThreshold: 3, //the number of ajax errors beyond which the get cycle should cease.
  ticker: null, //setTimeout reference - allows the get cycle to be cancelled with clearTimeout(ajaxUserMarkerObj.ticker);

  get: function () { //a function which initiates

      if (ajaxUserMarkerObj.errorCount < ajaxUserMarkerObj.errorThreshold) {
         ajaxUserMarkerObj.ticker = setTimeout(getMarkerData, ajaxUserMarkerObj.delay);
      }

  },

  fail: function (jqXHR, textStatus, errorThrown) {

      console.log(errorThrown);
      ajaxUserMarkerObj.errorCount++;
  }
};

//Ajax master routine

function getMarkerData() {

  $.ajax(ajaxUserMarkerObj.options)
      .done(updateUserMarker) //fires when ajax returns successfully
      .fail(ajaxUserMarkerObj.fail) //fires when an ajax error occurs
      .always(ajaxUserMarkerObj.get); //fires after ajax success or ajax error
}

function updateUserMarker(data) {

  // alert(data)
  coordinates = JSON.parse(data);
  user_lat = coordinates['lat'];
  user_lng = coordinates['lng'];
  if ((user_lat == null) || (user_lng == null)) {
    ajaxUserMarkerObj.errorCount++;

  //update users location on map
  } else {
    
    //create new user marker and plane trail if one doesnt already exist and info box
    if (userMarkerInfo.marker == null) {
      userMarkerInfo.marker = createNewUserMarker(user_lat,user_lng, map);
      userMarkerInfo.poly = createUserPlaneTrail(user_lat,user_lng, map);
      // var infowindow = new google.maps.InfoWindow();
      // infowindow.setContent('<span style="color:#EA2E49;font-weight:bold">' + userMarkerInfo.user_id + '</span>')
      
      // //Attach click listener to marker

      // google.maps.event.addListener(userMarkerInfo.marker, 'click', (function () {

      //     return function () {

      //         infowindow.setContent(userMarkerInfo.user_id);
      //         infowindow.open(map, userMarkerInfo.marker);

      //     }

      // }));

    } else {
      //update location of existing marker
      // userMarkerInfo.marker.setPosition(new google.maps.LatLng(-32.1, 154.0));
      userMarkerInfo.marker.setPosition(new google.maps.LatLng(user_lat, user_lng));

      //update user plane trail
      const path = userMarkerInfo.poly.getPath();

      // Because path is an MVCArray, we can simply append a new coordinate and it will automatically appear.
      path.push(new google.maps.LatLng(user_lat, user_lng));
    }
    map.panTo(userMarkerInfo.marker.getPosition()); 
  }
}

$("#show_positon").click(function() {
  
  // alert( "show position called." );
  getMarkerData()


  // $.ajax({
  //   type: 'POST',
  //   url: "/users/get_user_location",
  //   data: {user_id: 3},
  //   dataType: "text",
  //   success: function(data){
  //             coordinates = JSON.parse(data);
  //             user_lat = coordinates['lat']
  //             user_lng = coordinates['lng']
  //              alert("User location is "+ user_lat  + ', ' + user_lng);
  //   },
  //   error: function(error) {
  //       console.log(error);
  //   }
  // });
});

function createNewUserMarker(user_lat,user_lng, map) {

  label_txt = user_lat.toFixed(2).toString() + ' , ' + user_lng.toFixed(2).toString()
  marker = new google.maps.Marker({

    position: new google.maps.LatLng(user_lat, user_lng),
    icon: {
          url:'/static/img/marker/user_marker_airplane.png', //Marker icon.
          labelOrigin: new google.maps.Point(12, 45),
          
          },
    map: map,
    label:{
            text:label_txt,
            fontSize: "14px",
            fontWeight: "bold",
            color:'black',
            // fontFamily: '"Courier New", Courier,Monospace',
          },
    opacity:0.8,

  });

  return marker;

}

function createUserPlaneTrail(user_lat,user_lng, map) {
  // This converts a polyline to a dashed line, by
  // setting the opacity of the polyline to 0, and drawing an opaque symbol
  // at a regular interval on the polyline.
  const lineSymbol = {
    path: "M 0,-1 0,1",
    strokeOpacity: 1,
    scale: 4,
  };

  label_txt = user_lat.toFixed(2).toString() + ' , ' + user_lng.toFixed(2).toString()
  poly = new google.maps.Polyline({
    path: [
      { lat: user_lat, lng: user_lng },
    ],
    strokeColor: "#000000",
    strokeOpacity: 0,
    strokeWeight: 3,
    icons: [
      {
        icon: lineSymbol,
        offset: "0",
        repeat: "20px",
      },
    ],
  });
  poly.setMap(map);

  return poly;

}