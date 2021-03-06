
(function ($) {
"use strict";

$(document).ready(function(){

  // window.location.hash='where_togo_area';

  //  go to user detail tab that the user was last on upon refresh
  $('a[data-toggle="tab"]').on('show.bs.tab', function(e) {
    localStorage.setItem('activeTab', $(e.target).attr('href'));
  });
  var activeTab = localStorage.getItem('activeTab');
  if(activeTab){
      $('#user_pois_tabs a[href="' + activeTab + '"]').tab('show');
  }


  var search_returned_results = $('#searchResults').val();

  if (search_returned_results == 'False') {
    $("#search_results_flash").show();
    setTimeout(function() { $("#search_results_flash").hide(); }, 10000);
  }


  var poi_created = $('#poiCreated').val();

  if (poi_created == 'True') {
    $("#poi_created_flash").show();
    setTimeout(function() { $("#poi_created_flash").hide(); }, 10000);
  }

  var poi_updated = $('#poiUpdated').val();

  if (poi_updated == 'True') {
    $("#poi_updated_flash").show();
    setTimeout(function() { $("#poi_updated_flash").hide(); }, 10000);
  }
  

  // mobile_menu
  var menu = $('ul#navigation');
  if(menu.length){
    menu.slicknav({
      prependTo: ".mobile_menu",
      closedSymbol: '+',
      openedSymbol:'-'
    });
  };

  //check if name exists when creating new poi
  $(".form_new_poi #name").blur(function(){
    
  });

  $(document).on("click", ".iw_delete_poi", function () {
          
    var eventId = $(this).data('id');
    var form_action = '/poi/' + eventId + '/delete'+'?page=home'

    $("#delete_poi_confirm").attr('action', form_action);
    // console.log(eventId);
    $('#poi').html( eventId );
  });

  //handle for deleting a sim flight
  $(document).on("click", ".iw_delete_flight", function () {
          
    var eventId = $(this).data('id');
    var form_action = '/my_flights/delete/' + eventId +'?page=home'
    $("#delete_flight_confirm_btn").attr('action', form_action);
    // console.log(eventId);
    // $('#poi').html( eventId );
  });

  // $(document).on("click", "#deleteFlightModal", function () {
  //   $( "#flag_poi_confirm_btn" ).click(function() {
       
  //      var eventId = $('.iw_delete_flight').data('flight_id');
  //      var form_action = '/my_flights/delete/' + eventId +'?page=home'
  //      console.log(form_action)
  //      $.post('/my_flights/delete/' + eventId +'?page=home')
  //     //  $("#delete_flight_confirm").attr('action', form_action);
  //   //    $('#poi').html( eventId );
  // });

  //handle for flagging a POI
  $( "#flag_poi_confirm_btn" ).click(function() {

    var poi_id = $('.iw_delete_poi').data('id');
    var message = $('#flaggedModalFormReasonTextArea').val();

    if (message.length < 1) {
        $("#flag_poi_modal_form").addClass('was-validated');
    } else{
        // $('#flaggedModalFormReasonTextArea').val("");
        $('#flagReasonModal').modal('hide')
        $("#iw_flagged_poi_icon").removeClass("far").addClass("fas");
        $('#iw_flagged_poi_icon').prop('title', 'POI has been reported');
        $.post("/flag_poi", {"reason": message, "poi_id": poi_id, "page":'home'})
        flash_poi_flagged();
        add_flagged_poi_to_list(poi_id);
        $('html, body').animate({
            scrollTop: $("#poi_flagged_flash").offset().top
        }, 500);
        $(this).find('form').trigger('reset');
    }
  });

  $('#flagReasonModal' ).on('hidden.bs.modal', function() {

    $("#flag_poi_modal_form").removeClass('was-validated')
    $('#flaggedModalFormReasonTextArea').val("");
  })


  function flash_poi_flagged() {

    $("#poi_flagged_flash").show();
      setTimeout(function() { $("#poi_flagged_flash").hide(); }, 10000);
  }

  //Update Country Select values
  $("a.boxed-btn3").click(function(){

    // var country = $(this).parent().find("a").attr("data-value"); 
    var country = $(this).attr("data-value"); 
    $("#selectCountry").val(country)
    // $('#search_form').submit();
    $("#search_form_submit_btn").click()

  });

  // //close delete confirm modal after deletion
  // $('#delete_poi_confirm_btn').click(function(){
    
  //   $('#deleteModal').modal('hide');
  //   $(window).scrollTop(0);
    

  // });

  //Tab data table
  $('a[data-toggle="tab"]').on('shown.bs.tab', function(e){
    $($.fn.dataTable.tables({ visible: true, api: true })).DataTable()
       .columns.adjust()
       .responsive.recalc();
  });

  $('#account_poi_datatable').DataTable( {
    
    responsive: true,
    'columnDefs': [
    
      { className: 'text-center', targets: [1,2,4,5,6, 7] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         false
    
    // "pagingType": "full_numbers"
  } );

  $('#account_favorite_datatable').DataTable( {

    responsive: true,
    'columnDefs': [
    
      { className: 'text-center', targets: [1,2,4, 5] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         false
    // "pagingType": "full_numbers"
  } );

  $('#account_visited_datatable').DataTable( {

    responsive: true,
    'columnDefs': [
    
      { className: 'text-center', targets: [1,2,4, 5] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         false
    // "pagingType": "full_numbers"
  } );

  $('#account_flagged_datatable').DataTable( {

    responsive: true,
    'columnDefs': [
    
      { className: 'text-center', targets: [2,3] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         false
    // "pagingType": "full_numbers"
  } );

  $('#all_pois_datatable').DataTable( {
    
    'columnDefs': [
    
      { className: 'text-center', targets: [1,2, 4, 5, 7,8,9] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         false,
    "order": [[ 0, "desc" ]]
    // "pagingType": "full_numbers"
  } );

  $('#filtered_pois_datatable').DataTable( {
    
    'columnDefs': [
    
      { className: 'text-center', targets: [0,1,2, 3, 5,6] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         false,
    "order": [[ 2, "asc" ]],
    // "pagingType": "full_numbers"
  } );

  $('#all_users_datatable').DataTable( {
    
    'columnDefs': [
    
      { className: 'text-center', targets: [0,2,3,4,5,6,7] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         false
    // "pagingType": "full_numbers"
  } );

  $('#flagged_pois_datatable').DataTable( {
    
    'columnDefs': [
    
      { className: 'text-center', targets: [1, 5,6, 7,8] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         false
    // "pagingType": "full_numbers"
  } );

  $('#shared_flightplans_datatable').DataTable( {
    
    'columnDefs': [
    
      { className: 'text-center', targets: [0,1,2,4,5] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         false
    // "pagingType": "full_numbers"
  } );
  

  $('#account_user_fp_datatable').DataTable( {
    
    'columnDefs': [
    
      { className: 'text-center', targets: [2,3,4] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         false
    // "pagingType": "full_numbers"
  } );

  $('#account_user_flight_datatable').DataTable( {
    
    'columnDefs': [
    
      { className: 'text-center', targets: [4, 6, 7] },
      { type: 'date', 'targets': [0] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         false,
    order: [[ 0, 'desc' ]]
    // "pagingType": "full_numbers"
  } );

  $('#poi_popularity_datatable').DataTable( {
    
    'columnDefs': [
    
      { className: 'text-center', targets: [0,2,3,4,6] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         true,
    "order": [[0, 'desc']],
    "pageLength": 100,
    // "pagingType": "full_numbers"
  } );

  $('#flight_popularity_datatable').DataTable( {
    
    'columnDefs': [
    
      { className: 'text-center', targets: [0,3] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         true,
    "order": [[0, 'desc']],
    "pageLength": 25,
    // "pagingType": "full_numbers"
  } );

  $('#user_popularity_datatable').DataTable( {
    
    'columnDefs': [
    
      { className: 'text-center', targets: [1,2,3] },
    ],
    // "scrollY":        "800px",
    "scrollCollapse": true,
    "paging":         true,
    "order": [[1, 'desc']],
    "pageLength": 25,
    // "pagingType": "full_numbers"
  } );


  $('#topten_pois_datatable').DataTable( {

    
    'columnDefs': [
    
      { className: 'text-center', targets: [4,5] },
    ],

    "searching": false,
    "paging": false,
    "info": false,
    "order": [[4, 'desc']]
    // "scrollY":        "800px",
    // "scrollCollapse": true,
    // "paging":         false
    // "pagingType": "full_numbers"
  } );

    
  // review-active
  $('.slider_active').owlCarousel({
    loop:true,
    margin:0,
    items:1,
    autoplay:true,
    navText:['<i class="ti-angle-left"></i>','<i class="ti-angle-right"></i>'],
    nav:true,
    dots:false,
    autoplayHoverPause: true,
    autoplaySpeed: 800,
    animateOut: 'fadeOut',
    animateIn: 'fadeIn',
    responsive:{
        0:{
            items:1,
            nav:false,
        },
        767:{
            items:1
        },
        992:{
            items:1
        },
        1200:{
            items:1
        },
        1600:{
            items:1
        }
    }
  });

  // review-active
  $('.testmonial_active').owlCarousel({
    loop:true,
    margin:0,
    items:1,
    autoplay:true,
    navText:['<i class="ti-angle-left"></i>','<i class="ti-angle-right"></i>'],
    nav:false,
    dots:true,
    autoplayHoverPause: true,
    autoplaySpeed: 800,
    responsive:{
        0:{
            items:1,
        },
        767:{
            items:1,
        },
        992:{
            items:1,
        },
        1200:{
            items:1,
        },
        1500:{
            items:1
        }
    }
  });

  $( function() {
    $( "#slider-range" ).slider({
        range: true,
        min: 0,
        max: 600,
        values: [ 75, 300 ],
        slide: function( event, ui ) {
            $( "#amount" ).val( "$" + ui.values[ 0 ] + " - $" + ui.values[ 1 ] );
        }
    });
    $( "#amount" ).val( "$" + $( "#slider-range" ).slider( "values", 0 ) +
        " - $" + $( "#slider-range" ).slider( "values", 1 ) );
  } );


  // for filter
  // init Isotope
  var $grid = $('.grid').isotope({
    itemSelector: '.grid-item',
    percentPosition: true,
    masonry: {
      // use outer width of grid-sizer for columnWidth
      columnWidth: 1
    }
  });

  // filter items on button click
  $('.portfolio-menu').on('click', 'button', function () {
    var filterValue = $(this).attr('data-filter');
    $grid.isotope({ filter: filterValue });
  });

  //for menu active class
  $('.portfolio-menu button').on('click', function (event) {
    $(this).siblings('.active').removeClass('active');
    $(this).addClass('active');
    event.preventDefault();
	});
  
  // wow js
  new WOW().init();

  // counter 
  $('.counter').counterUp({
    delay: 10,
    time: 10000
  });

  /* magnificPopup img view */
  $('.popup-image').magnificPopup({
    type: 'image',
    gallery: {
      enabled: true
    }
  });

  /* magnificPopup img view */
  $('.img-pop-up').magnificPopup({
    type: 'image',
    gallery: {
      enabled: true
    }
  });

  /* magnificPopup video view */
  $('.popup-video').magnificPopup({
    type: 'iframe'
  });


  // scrollIt for smoth scroll
  $.scrollIt({
    upKey: 38,             // key code to navigate to the next section
    downKey: 40,           // key code to navigate to the previous section
    easing: 'linear',      // the easing function for animation
    scrollTime: 600,       // how long (in ms) the animation takes
    activeClass: 'active', // class given to the active nav element
    onPageChange: null,    // function(pageIndex) that is called when page is changed
    topOffset: 0           // offste (in px) for fixed top navigation
  });

  // scrollup bottom to top
  $.scrollUp({
    scrollName: 'scrollUp', // Element ID
    topDistance: '4500', // Distance from top before showing element (px)
    topSpeed: 300, // Speed back to top (ms)
    animation: 'fade', // Fade, slide, none
    animationInSpeed: 200, // Animation in speed (ms)
    animationOutSpeed: 200, // Animation out speed (ms)
    scrollText: '<i class="fa fa-angle-double-up"></i>', // Text for element
    activeOverlay: false, // Set CSS color to display scrollUp active point, e.g '#00FFFF'
  });


    // blog-page

    //brand-active
  $('.brand-active').owlCarousel({
    loop:true,
    margin:30,
  items:1,
  autoplay:true,
    nav:false,
  dots:false,
  autoplayHoverPause: true,
  autoplaySpeed: 800,
    responsive:{
        0:{
            items:1,
            nav:false

        },
        767:{
            items:4
        },
        992:{
            items:7
        }
    }
  });

  // blog-dtails-page

    //project-active
  $('.project-active').owlCarousel({
    loop:true,
    margin:30,
  items:1,
  // autoplay:true,
  navText:['<i class="Flaticon flaticon-left-arrow"></i>','<i class="Flaticon flaticon-right-arrow"></i>'],
  nav:true,
  dots:false,
  // autoplayHoverPause: true,
  // autoplaySpeed: 800,
    responsive:{
        0:{
            items:1,
            nav:false

        },
        767:{
            items:1,
            nav:false
        },
        992:{
            items:2,
            nav:false
        },
        1200:{
            items:1,
        },
        1501:{
            items:2,
        }
    }
  });

  if (document.getElementById('default-select')) {
    $('select').niceSelect();
  }

    //about-pro-active
  $('.details_active').owlCarousel({
    loop:true,
    margin:0,
  items:1,
  // autoplay:true,
  navText:['<i class="ti-angle-left"></i>','<i class="ti-angle-right"></i>'],
  nav:true,
  dots:false,
  // autoplayHoverPause: true,
  // autoplaySpeed: 800,
    responsive:{
        0:{
            items:1,
            nav:false

        },
        767:{
            items:1,
            nav:false
        },
        992:{
            items:1,
            nav:false
        },
        1200:{
            items:1,
        }
    }
  });

});

//------- Mailchimp js --------//  
function mailChimp() {
  $('#mc_embed_signup').find('form').ajaxChimp();
}
mailChimp();



        // Search Toggle
        $("#search_input_box").hide();
        $("#search").on("click", function () {
            $("#search_input_box").slideToggle();
            $("#search_input").focus();
        });
        $("#close_search").on("click", function () {
            $('#search_input_box').slideUp(500);
        });
        // Search Toggle
        $("#search_input_box").hide();
        $("#search_1").on("click", function () {
            $("#search_input_box").slideToggle();
            $("#search_input").focus();
        });
        // $(document).ready(function() {
        //   $('select').niceSelect();
        // });

        // prise slider 
        

})(jQuery);	




