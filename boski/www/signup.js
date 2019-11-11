/*
	Developer: Kartik Sharma
 	Email: kartik.sharma@grynn.in
*/

frappe.ready(function() {
    let $page = $('#page-signup, #page-signup-1');

    //setup route
    document.onload = checkLocationHash();
    window.onhashchange = changeRoute;

    function getRoutingInfo(route) {
        for (var ii = 0; ii < route_map.length; ii++) {
            if (route_map[ii].route == route) {
                return route_map[ii];
            }
        }
    }

    function showElement(route) {
        for (var ii = 0; ii < route_map.length; ii++) {
            $page.find(route_map[ii].element).addClass('hide');
        }
        $page.find(route).removeClass('hide');
    }

    function changeRoute(stage) {
        set_stage(stage)
        currentRoute = getRoutingInfo(location.hash);
        showElement(currentRoute.element);
    }

    function set_stage(stage) {
        window.scroll(0, 0);

        let slides = {
            "verify-email": {
                "stage": "stage-2",
                "addclass": 'personal-setup',
                "removeclass": 'stage-1'
            },
            "regional-setup": {
                "stage": "stage-3",
                "addclass": 'verify-email',
                "removeclass": 'stage-2'
            },
            "business-setup": {
                "stage": "stage-4",
                "addclass": 'regional-setup',
                "removeclass": 'stage-3'
            }
        };

        if (stage && slides[stage]) {
            $page.find('.' + slides[stage]['stage'] + '').addClass('completed');
            $page.find('.' + stage + '').removeClass('text-extra-muted');

            $page.find('.' + slides[stage]['removeclass'] + '').removeClass('completed');
            $page.find('.' + slides[stage]['addclass'] + '').addClass('text-extra-muted');
        }
    }

    function checkLocationHash() {
        if (location.hash === "" || location.hash === "#") {
            location.hash = "#personal-details"
        }
        changeRoute()
    }

    // Define the signup stages
    setup_signup($('#page-signup'));

    //  Check for valid email
    $page.find('input[name="email"]').on('change', function() {
        let email = $(this).val();
        if (!valid_email(email)) {
            $(this).closest('.form-group').addClass('invalid');
        } else {
            $(this).closest('.form-group').removeClass('invalid');
        }
    });

    // Check if form is completed and all values are valid
    $page.find('.get-started-button').on('click', ()=>{
        setup_account_request($page, changeRoute);
    }
    );

    $page.find('.btn-request').on('click', ()=>{
        verify_otp($page, changeRoute);
    }
    )

    $page.find('.btn-resend-otp').on('click', ()=>{
        resend_otp($page);
    }
    )
    
    $page.find('.initiate').on('click', ()=>{
        initiate($page);
    }
    );

    $page.find('.other-details').ready(function(){
        let users = $page.find('input[name="number_of_users"]').val();
        let currency = $page.find('select[name="currency"]').val();
        let billing_cycle = $page.find('#billing_cycle').val();
        
        get_total_cost($page);

    })

    $page.find('select[name="currency"]').on('change', ()=>{
        get_total_cost($page);
    })
    $page.find('input[name="number_of_users"]').on('change', ()=>{
        get_total_cost($page);
    })
    $page.find('#billing_cycle').on('change', ()=>{
        get_total_cost($page);
    })    

    $page.find('.apply-code').on('click', ()=>{
        get_total_cost($page);
        if (!$page.find('input[name="coupon"]').val()){    
            frappe.msgprint("Please enter a coupon code first.");
        }
    })

    $page.find('.plan-select-button').on('click', ()=>{
        if (!$page.find('select[name="currency"]').val() || !$page.find('input[name="users"]').val() /*|| !$page.find('input[name="designation"]').val() || !$page.find('select[name="referral_source"]').val()*/) {

            frappe.msgprint("All fields are necessary. Please try again.");
            return false;
        } else {
            setup_other_details($page, changeRoute);
        }
    }
    );

    $page.find('.account-setup-button').on('click', ()=>{
        if (!$page.find('select[name="country"]').val() || !$page.find('select[name="industry_type"]').val() || !$page.find('select[name="currency"]').val() || !$page.find('select[name="language"]').val() || !$page.find('select[name="timezone"]').val()) {

            frappe.msgprint("All fields are necessary. Please try again.");
            return false;
        } else {
            setup_regional_details($page, changeRoute);
        }
    }
    );
});

const route_map = [{
    route: "#verify",
    element: ".verify-otp"
},{
    route: "#personal-details",
    element: ".personal-info"
},{
    route: "#other-details",
    element: ".other-details"
}]

setup_signup = function(page) {
    // button for signup event
    if (!page) {
        // fallback
        var page = $('#page-signup,#page-signup-1');
    }

    $('input[name="number_of_users"]').val(1);

    $('input[name="number_of_users"]').on('change', function() {
        let number_of_users = Number($(this).val());

        if (isNaN(number_of_users) || number_of_users <= 0) {
            $(this).closest('.form-group').addClass('invalid');
        } else {
            $(this).closest('.form-group').removeClass('invalid');

            $('.number_of_users').html(number_of_users);
            $('.user-text').html(number_of_users > 1 ? 'users' : 'user');
        }
    });

    //-------------------------------------- Subdoamin Validation and Avalability Check -----------------------------

    page.find('input[name="subdomain"]').on('input', function() {
        domain_input_flag = 1;
        var $this = $(this);
        clearTimeout($this.data('timeout'));
        $this.data('timeout', setTimeout(function() {
            let subdomain = $this.val().toLowerCase();
            set_availability_status('empty');
            if (subdomain.length === 0) {
                return;
            }

            page.find('.availability-status').addClass('hidden');
            var [is_valid,validation_msg] = is_a_valid_subdomain(subdomain);
            if (is_valid) {
                // show spinner
                page.find('.availability-spinner').removeClass('hidden');
                check_if_available(subdomain, function(status) {
                    set_availability_status(status, subdomain);
                    // hide spinner
                    page.find('.availability-spinner').addClass('hidden');
                });
            } else {
                set_availability_status('invalid', subdomain, validation_msg);
            }
        }, 500));
    });

    function set_availability_status(is_available, subdomain, validation_msg) {
        // reset
        page.find('.availability-status').addClass('hidden');
        page.find('.signup-subdomain').removeClass('invalid');

        if (typeof is_available === 'string') {
            if (is_available === 'empty') {// blank state
            } else if (is_available === 'invalid') {
                // custom validation message
                const form_control = page.find('.signup-subdomain').addClass('invalid');
                form_control.find('.validation-message').html(validation_msg || '');
            }
            return;
        }

        page.find('.availability-status').removeClass('hidden');
        if (is_available) {
            // available state
            page.find('.availability-status i').removeClass('octicon-x text-danger');
            page.find('.availability-status i').addClass('octicon-check text-success');

            page.find('.availability-status').removeClass('text-danger');
            page.find('.availability-status').addClass('text-success');
            page.find('.availability-status span').html(`${subdomain}.grynn.ch is available!`);
            toggle_create_button(false);
        } else {
            // not available state
            page.find('.availability-status i').removeClass('octicon-check text-success');
            page.find('.availability-status i').addClass('octicon-x text-danger');

            page.find('.availability-status').removeClass('text-success');
            page.find('.availability-status').addClass('text-danger');
            page.find('.availability-status span').html(`${subdomain}.grynn.ch is already taken.`);
            toggle_create_button(true);
        }
    }

    page.find('.btn-request').off('click').on('click', function() {
    });

    // change help description based on subdomain change
    $('[name="subdomain"]').on("keyup", function() {
        $('.subdomain-help').text($(this).val() || window.erpnext_signup.subdomain_placeholder);
    });


    function is_a_valid_subdomain(subdomain) {
        var MIN_LENGTH = 4;
        var MAX_LENGTH = 20;
        if (subdomain.length < MIN_LENGTH) {
            return [0, `Sub-domain cannot have less than ${MIN_LENGTH} characters`];
        }
        if (subdomain.length > MAX_LENGTH) {
            return [0, `Sub-domain cannot have more than ${MAX_LENGTH} characters`];
        }
        if (subdomain.search(/^[A-Za-z0-9][A-Za-z0-9]*[A-Za-z0-9]$/) === -1) {
            return [0, 'Sub-domain can only contain letters and numbers'];
        }
        return [1, ''];
    }

    function check_if_available(subdomain, callback) {
        setTimeout(function() {
            frappe.call({
                method: 'boski.utils.boski.check_site_name',
                args: {
                    site: subdomain
                },
                type: 'POST',
                callback: function(r) {
                    if (!r.message) {
                        callback(1);
                    } else {
                        callback(0);
                    }
                },
            });
        }, 2000);
    }

    window.clear_timeout = function() {
        if (window.timout_password_strength) {
            clearTimeout(window.timout_password_strength);
            window.timout_password_strength = null;
        }
    }
    ;

    //-------------------------------------- Password Strength --------------------------------------
    window.strength_indicator = $('.password-strength-indicator');
    window.strength_message = $('.password-strength-message');

    $('#passphrase').on('keyup', function() {
        window.clear_timeout();
        window.timout_password_strength = setTimeout(test_password_strength, 200);
    });

    function test_password_strength() {
        window.timout_password_strength = null;
        return frappe.call({
            type: 'GET',
            method: 'frappe.core.doctype.user.user.test_password_strength',
            args: {
                new_password: $('#passphrase').val()
            },
            callback: function(r) {
                if (r.message) {
                    var score = r.message.score
                      , feedback = r.message.feedback;

                    feedback.crack_time_display = r.message.crack_time_display;
                    feedback.score = score;

                    if (feedback.password_policy_validation_passed) {
                        set_strength_indicator('green', feedback);
                        $('input[name="passphrase"]').closest('.form-group').removeClass('invalid');
                    } else {
                        set_strength_indicator('red', feedback);
                        $('input[name="passphrase"]').closest('.form-group').addClass('invalid');
                    }
                }
            }
        });
    }

    function set_strength_indicator(color, feedback) {
        var message = [];
        feedback.help_msg = "";
        if (!feedback.password_policy_validation_passed) {
            feedback.help_msg = "<br>" + "Hint: Include symbols, numbers and capital letters in the password";
        }
        if (feedback) {
            if (!feedback.password_policy_validation_passed) {
                if (feedback.suggestions && feedback.suggestions.length) {
                    message = message.concat(feedback.suggestions);
                } else if (feedback.warning) {
                    message.push(feedback.warning);
                }
                message.push(feedback.help_msg);

            } else {
                message.push("Success! You are good to go 👍");
            }
        }

        strength_indicator.removeClass().addClass('password-strength-indicator indicator ' + color);
        strength_message.html(message.join(' ') || '').removeClass('hidden');
        // strength_indicator.attr('title', message.join(' ') || '');
    }
}
;

function setup_account_request($page, changeRoute) {
    if (!$page.find('input[name="first_name"]').val() || !$page.find('input[name="last_name"]').val() || !$page.find('input[name="email"]').val() /*|| !$page.find('input[name="passphrase"]').val()*/) {

        frappe.msgprint("All fields are necessary. Please try again.");
        return false;

    } else if ($page.find('input[name="email"]').parent().hasClass('invalid')) {

        frappe.msgprint("Please enter a valid email.");
        return false;

    } else if ($page.find('input[name="passphrase"]').parent().hasClass('invalid')) {

        frappe.msgprint("Please enter a strong password.");
        return false;

    } else {
        var args = Array.from($page.find('.personal-info form input')).reduce((acc,input)=>{
            acc[$(input).attr('name')] = $(input).attr('name')  === "subdomain" ? $(input).val().trim().toLowerCase() : $(input).val().trim() ;
            return acc;
        }
        , {});
        // validate inputs
        const validations = Array.from($page.find('.form-group.invalid')).map(form_group=>$(form_group).find('.validation-message').html());
        if (validations.length > 0) {
            frappe.msgprint(validations.join("<br>"));
            return;
        }

        frappe.call({
            method: 'boski.www.signup.signup',
            args: args,
            type: 'POST',
            // btn: $btn,
            callback: function(r) {
                if (r.exc)
                    return;

                if (r.message.location) {
                    location.hash = r.message.location;
                    localStorage.setItem("reference", r.message.reference);
                    localStorage.setItem("email", r.message.email);
                    $('.verify-otp .email').text(r.message.email);
                    changeRoute('verify-email');
                }
            },

        })
        return false;

    }
}

function verify_otp($page, changeRoute) {
    if (!$page.find('input[name="otp"]').val()) {
        frappe.msgprint("Verification Code can't be empty!")
        return false;
    }

    var args = Array.from($page.find('.verify-otp form input')).reduce((acc,input)=>{
        acc[$(input).attr('name')] = $(input).val().trim();
        return acc;
    }
    , {});
    args['id'] = localStorage.getItem("reference");

    var $btn = $page.find('.btn-request');
    var btn_html = $btn.html();
    $btn.prop("disabled", true).html("Verifying details...");

    frappe.call({
        method: 'boski.www.signup.verify_otp',
        args: args,
        type: 'POST',
        btn: $btn,
        callback: function(r) {
            if (r.exc)
                return;

            if (r.message.location) {
                location.hash = r.message.location;
                changeRoute('regional-setup');
            }
        },
    }).always(function() {
        $btn.prop("disabled", false).html(btn_html);
    });
}

function resend_otp($page) {
    var $btn = $page.find('.btn-resend-otp');
    var btn_html = $btn.html();
    $btn.prop("disabled", true).html("Resending verfication code...");
    let args = {};
    args['email'] = localStorage.getItem("email");
    frappe.call({
        method: 'boski.www.signup.resend_otp',
        args: {args},
        type: 'POST',
        btn: $btn,
    }).always(function() {
        $btn.prop("disabled", false).html(btn_html);
    });
}

function setup_regional_details($page, changeRoute) {
    var args = Array.from($page.find('.regional-settings form select')).reduce((acc,input)=>{
        acc[$(input).attr('name')] = $(input).val();
        return acc;
    }
    , {});
    args['id'] = localStorage.getItem("reference");
    args['domain'] = args['industry_type'];

    var $btn = $page.find('.account-setup-button');
    var btn_html = $btn.html();
    $btn.prop("disabled", true).html("Updating...");

    frappe.call({
        method: 'central.www.prepare_site.update_account_request',
        args: args,
        type: 'POST',
        btn: $btn,
        callback: function(r) {
            if (r.exc)
                return;

            if (r.message.location) {
                location.hash = r.message.location;
                changeRoute('business-setup');
            }
        },
    }).always(function() {
        $btn.prop("disabled", false).html(btn_html);
    });
}

function setup_other_details($page, changeRoute) {
    var args = Array.from($page.find('.other-details form input, .other-details form select')).reduce((acc,input)=>{
        acc[$(input).attr('name')] = $(input).val();
        return acc;
    }
    , {});
    args['id'] = localStorage.getItem("reference");

    if (cint(args['users']) < 1 || cint(args['users']) > 100000) {
        frappe.msgprint("Please select number of users between range 1 to 100000");
        return false;
    }

    var $btn = $page.find('.other-settings-button');
    var btn_html = $btn.html();
    $btn.prop("disabled", true).html("Updating...");

    frappe.call({
        method: 'central.www.prepare_site.update_account_request',
        args: args,
        type: 'POST',
        btn: $btn,
        callback: function(r) {
            if (r.exc)
                return;

            if (r.message.location) {
                window.location.href = r.message.location
                changeRoute();
            }
        },
    }).always(function() {
        $btn.prop("disabled", false).html(btn_html);
    });
}

window.erpnext_signup = {
    subdomain_placeholder: 'mycompany',
    distribution: 'erpnext'
}

function toggle_button(event) {
    let button = $(".initiate");
    button.prop("disabled", !event.target.checked);
    ;
}
function toggle_create_button(value) {
    let button = $(".get-started-button");
    button.prop("disabled", value);
}
function get_args($page){
    let users = $page.find('input[name="number_of_users"]').val();
    let currency = $page.find('select[name="currency"]').val();
    let billing_cycle = $page.find('#billing_cycle').val();
    let coupon = $page.find('input[name="coupon"]').val() || "";
    
    let args = {};
    args['users'] = users;
    args['currency'] = currency;
    args['billing_cycle'] = billing_cycle;
    args['coupon'] = coupon;
    args['email'] = localStorage.getItem('email')
    return args;
}

function get_total_cost($page){
    let args = get_args($page);
    
    frappe.call({
        method: 'boski.www.signup.get_total_cost',
        args: args,
        type: 'POST',
        callback: function(r) {
            if (r.exc)
                return;
            $page.find('.summary').removeClass('hidden');
            if (r.message.billing_cost) {
                $('.billing').text(r.message.billing_cost);
                $('.billing-plan').text($page.find('#billing_cycle option:selected').text());

            }
            if (r.message.total_cost) {
                $('.total').text(r.message.total_cost);
            }
            if (r.message.discount) {
                $('.discount').text(r.message.discount);
            }
        },
    })
}

function initiate($page){
    let args = get_args($page);
    var $btn = $page.find('.get-started-button');
    var btn_html = $btn.html();
    $btn.prop("disabled", true).html("Sending details...");

    frappe.call({
        method: 'boski.www.signup.register',
        args: {args},
        type: 'POST',
        callback: function(r) {
            if (r.exc)
                return;
            window.location.href = r.message;
        },
    })
}
