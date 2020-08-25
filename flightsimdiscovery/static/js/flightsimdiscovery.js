/**
 * FLight Sim Discovery Javascript file
 * ScrollIt.js(scroll•it•dot•js) makes it easy to make long, vertically scrolling pages.
 *
 */

//  const countryList = [
//     "Afghanistan",
//     "Albania",
//     "Algeria",
//     "American Samoa",
//     "Andorra",
//     "Angola",
//     "Anguilla",
//     "Antarctica",
//     "Antigua and Barbuda",
//     "Argentina",
//     "Armenia",
//     "Aruba",
//     "Australia",
//     "Austria",
//     "Azerbaijan",
//     "Bahamas",
//     "Bahrain",
//     "Bangladesh",
//     "Barbados",
//     "Belarus",
//     "Belgium",
//     "Belize",
//     "Benin",
//     "Bermuda",
//     "Bhutan",
//     "Bolivia",
//     "Bosnia and Herzegovina",
//     "Botswana",
//     "Brazil",
//     "British Indian Ocean Territory",
//     "British Virgin Islands",
//     "Brunei",
//     "Bulgaria",
//     "Burkina Faso",
//     "Burundi",
//     "Cabo Verde",
//     "Cambodia",
//     "Cameroon",
//     "Canada",
//     "Cayman Islands",
//     "Central African Republic",
//     "Chad",
//     "Chile",
//     "China",
//     "Christmas Island",
//     "Cocos (Keeling) Islands",
//     "Colombia",
//     "Comoros",
//     "Congo",
//     "Congo, Democratic Republic of the",
//     "Cook Islands",
//     "Costa Rica",
//     "Croatia",
//     "Cuba",
//     "Cyprus",
//     "Czechia",
//     "Denmark",
//     "Djibouti",
//     "Dominica",
//     "Dominican Republic",
//     "Ecuador",
//     "Egypt",
//     "El Salvador",
//     "Equatorial Guinea",
//     "Eritrea",
//     "Estonia",
//     "Eswatini",
//     "Ethiopia",
//     "Falkland Islands (Malvinas)",
//     "Faroe Islands",
//     "Fiji",
//     "Finland",
//     "France",
//     "French Guiana",
//     "French Oceania",
//     "French Southern Territories",
//     "Gabon",
//     "Gambia",
//     "Georgia",
//     "Germany",
//     "Ghana",
//     "Gibraltar",
//     "Great Britain",
//     "Greece",
//     "Greenland",
//     "Grenada",
//     "Guadeloupe",
//     "Guam",
//     "Guatemala",
//     "Guernsey",
//     "Guinea",
//     "Guinea-Bissau",
//     "Guyana",
//     "Haiti",
//     "Heard Island and McDonald Islands",
//     "Honduras",
//     "Hong Kong",
//     "Hungary",
//     "Iceland",
//     "India",
//     "Indonesia",
//     "Iran",
//     "Iraq",
//     "Ireland",
//     "Isle of Man",
//     "Israel",
//     "Italy",
//     "Ivory Coast",
//     "Jamaica",
//     "Japan",
//     "Jersey",
//     "Jordan",
//     "Kazakhstan",
//     "Kenya",
//     "Kiribati",
//     "Kosovo",
//     "Kuwait",
//     "Kyrgyzstan",
//     "Laos",
//     "Latvia",
//     "Lebanon",
//     "Lesotho",
//     "Liberia",
//     "Libya",
//     "Liechtenstein",
//     "Lithuania",
//     "Luxembourg",
//     "Macao",
//     "Madagascar",
//     "Malawi",
//     "Malaysia",
//     "Maldives",
//     "Mali",
//     "Malta",
//     "Marshall Islands",
//     "Martinique",
//     "Mauritania",
//     "Mauritius",
//     "Mayotte",
//     "Mexico",
//     "Moldova, Republic of",
//     "Monaco",
//     "Mongolia",
//     "Montenegro",
//     "Montserrat",
//     "Morocco",
//     "Mozambique",
//     "Myanmar",
//     "Namibia",
//     "Nauru",
//     "Nepal",
//     "Netherlands",
//     "New Caledonia",
//     "New Zealand",
//     "Nicaragua",
//     "Niger",
//     "Nigeria",
//     "Niue",
//     "Norfolk Island",
//     "North Korea",
//     "North Macedonia",
//     "Northern Mariana Islands",
//     "Norway",
//     "Oceania (Federated States of)",
//     "Oman",
//     "Pakistan",
//     "Palau",
//     "Palestine, State of",
//     "Panama",
//     "Papua New Guinea",
//     "Paraguay",
//     "Peru",
//     "Philippines",
//     "Pitcairn",
//     "Poland",
//     "Portugal",
//     "Puerto Rico",
//     "Qatar",
//     "Reunion",
//     "Romania",
//     "Russian Federation",
//     "Rwanda",
//     "Saint Barthélemy",
//     "Saint Helena",
//     "Saint Kitts and Nevis",
//     "Saint Lucia",
//     "Saint Pierre and Miquelo",
//     "Saint Vincent and the Grenadines",
//     "Samoa",
//     "San Marino",
//     "Sao Tome and Principe",
//     "Saudi Arabia",
//     "Senegal",
//     "Serbia",
//     "Seychelles",
//     "Sierra Leone",
//     "Singapore",
//     "Slovakia",
//     "Slovenia",
//     "Solomon Islands",
//     "Somalia",
//     "South Africa",
//     "South Georgia",
//     "South Korea",
//     "South Sudan",
//     "Spain",
//     "Sri Lanka",
//     "Sudan",
//     "Suriname",
//     "Svalbard and Jan Mayen",
//     "Swaziland",
//     "Sweden",
//     "Switzerland",
//     "Syria",
//     "Taiwan",
//     "Tajikistan",
//     "Tanzania",
//     "Thailand",
//     "Timor-Leste",
//     "Togo",
//     "Tokelau",
//     "Tonga",
//     "Trinidad and Tobago",
//     "Tunisia",
//     "Turkey",
//     "Turkmenistan",
//     "Turks and Caicos Islands",
//     "Tuvalu",
//     "U.S. Virgin Islands",
//     "Uganda",
//     "Ukraine",
//     "United Arab Emirates",
//     "United States of America",
//     "Uruguay",
//     "Uzbekistan",
//     "Vanuatu",
//     "Venezuela",
//     "VietNam",
//     "Wallis and Futuna",
//     "Western Sahara",
//     "Yemen",
//     "Zambia",
//     "Zimbabwe"
//   ];

//   const regionList = [
//   "Africa - Eastern",
//   "Africa - Middle",
//   "Africa - Northern",
//   "Africa - Southern",
//   "Africa - Western",
//   "America - Central",
//   "America - Northern",
//   "America - South",
//   "Antartica",
//   "Asia - Central",
//   "Asia - Eastern",
//   "Asia - South-eastern",
//   "Asia - Southern",
//   "Asia - Western",
//   "Caribbean",
//   "Europe - Eastern",
//   "Europe - Northern",
//   "Europe - Southern",
//   "Europe - Western",
//   "Oceania"
//   ];

const categoryList = [
  "Building",
  "Bush Strips",
  "Canyon",
  "City/town",
  "Dessert",
  "Helipads",
  "Infrastructure",
  "Interesting",
  "Island",
  "Lake",
  "Mountain",
  "National Park",
  "Other",
  "Reef",
  "River",
  "Seaports",
  "Seaports",
  "Volcano",
  "Waterfall",
];

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
  "Europe - Southern ": [
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
  "Africa - Northern ": [
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
    "French Oceania",
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

// //  Populate the where you want to explore dropdowns
// var select = document.getElementById("selectCategory");
// // var options = ["1", "2", "3", "4", "5"];
// for (var i = 0; i < categoryList.length; i++) {
//   var opt = categoryList[i];
//   var el = document.createElement("option");
//   el.textContent = opt;
//   el.value = opt.trim();
//   select.appendChild(el);
// }

// //  Populate the where you want to explore dropdowns
// var select = document.getElementById("selectRegion");
// // var options = ["1", "2", "3", "4", "5"];
// var regionList = Object.keys(region_country).sort();

// for (var i = 0; i < regionList.length; i++) {
//   var opt = regionList[i];
//   var el = document.createElement("option");
//   el.textContent = opt;
//   el.value = opt;
//   select.appendChild(el);
// }

// //  Populate the where you want to explore dropdowns
// var select = document.getElementById("selectCountry");
// var countryList = [];
// for (var region in region_country) {
//   Array.prototype.push.apply(countryList, region_country[region]);
//   countryList.sort();
// }

// console.log(countryList);

// for (var i = 0; i < countryList.length; i++) {
//   var opt = countryList[i];
//   var el = document.createElement("option");
//   el.textContent = opt;
//   el.value = opt;
//   select.appendChild(el);
// }

//add change listener on region dropdown to dynamically update country
$("#selectRegion")
  .change(function () {
    console.log(this.value.trim());

    
    // get the second dropdown
    $("#selectCountry").html(
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
  
  
	
	$('#selectCountry').prepend(new Option("Country", "Country"))
  // set default value
  $('#selectCountry').val('Country');

  }).change();
