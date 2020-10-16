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
    
    if (this.value.trim()!='Region') {
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
        $.each(countryList, function(i, p) {
        $('#selectCountry').append($('<option></option>').val(p).html(p));
        });

        // set default value
        $('#selectCountry').val("Country");

    }     

  })

  // set default value
  $('#selectCountry').val(country_default);

  function getCountryList(){

    countryList = [];
    // for (var i = 0; i < region_country.length; i++) {
      for (const [ region, regions_countries ] of Object.entries(region_country)) {
        // var regions_countries = value;
        // console.log(regions_countries);
        Array.prototype.push.apply(countryList, regions_countries);
        countryList.sort();
    }
    // console.log(countryList);
    return countryList;
  }
  

