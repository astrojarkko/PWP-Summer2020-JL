//  NOTE: this file is heavily based on the full example given in the course exercices
//
// Large changes have been made to adapt it to the routetracker API.


"use strict";

// constants
const DEBUG = true;
const MASONJSON = "application/vnd.mason+json";
const PLAINJSON = "application/json";


// render error handling function
function renderError(jqxhr) {
    let msg = jqxhr.responseJSON["@error"]["@message"];
    $("div.notification").html("<p class='error'>" + msg + "</p>");
}

// render message..
function renderMsg(msg) {
    $("div.notification").html("<p class='msg'>" + msg + "</p>");
}


//  for GET requests to retrieve the body and direct to next function
function getResource(href, renderer) {
    $.ajax({
        url: href,
        success: renderer,
        error: renderError
    });
}

// for POST or PUT methods to send the data to server
function sendData(href, method, item, postProcessor) {
    $.ajax({
        url: href,
        type: method,
        data: JSON.stringify(item),
        contentType: PLAINJSON,
        processData: false,
        success: postProcessor,
        error: renderError
    });
}


// user row function to show the information of an user in the DB
function userRow(item) {
    let link = "<a href='" +
                item["@controls"].self.href +
                "' onClick='followLink(event, this, renderUser)'>show</a>";

    return "<tr><td>" + item.email +
            "</td><td>" + item.firstName +
            "</td><td>" + item.lastName +
            "</td><td>" + link + "</td></tr>";
}


// route row function to show the information of a single route in the DB
// NOTE: each row now has also links that direct to specific links/actions of that route
function routeRow(item) {
    let locationCell = "<a href='" +
                item["@controls"]["locations:in-location"].href +
                "' onClick='followLink(event, this, renderRoutesSubset)'>"+item.location+"</a>";
    let disciplineCell = "<a href='" +
                item["@controls"]["disciplines:in-discipline"].href +
                "' onClick='followLink(event, this, renderRoutesSubset)'>"+item.discipline+"</a>";
    let gradeCell = "<a href='" +
                item["@controls"]["grades:in-grade"].href +
                "' onClick='followLink(event, this, renderRoutesSubset)'>"+item.grade+"</a>";
    let editCell = "<a href='" +
                item["@controls"]["routes:edit-route"].href +
                "' onClick='followLink(event, this, renderRouteEdit)'>edit</a>";
    let deleteCell = "<a href='" +
                item["@controls"]["routes:edit-route"].href +
                "' onClick='followLink(event, this, renderRouteDelete)'>delete</a>";

    return "<tr><td>" + item.date +
           "</td><td>" + locationCell +
           "</td><td>" + disciplineCell +
           "</td><td>" + gradeCell +
           "</td><td>" + item.extraInfo +
           "</td><td>" + editCell +
           "</td><td>" + deleteCell + "</td></tr>";
}


// route row function to show the information of a single route in the DB,
// has no links for simplicity
function routeRowSubset(item) {
    return "<tr><td>" + item.date +
           "</td><td>" + item.location +
           "</td><td>" + item.discipline +
           "</td><td>" + item.grade +
           "</td><td>" + item.extraInfo + "</tr>";
}


// route row function to show the values in one of the main route subsets (locations, disciples, or grades)
// makes links that then take to a list of routes in that subset
function routeItemRow(item) {
    if (item.location !== undefined) {
      var value = "<a href='" +
                  item["@controls"]["locations:in-location"].href +
                  "' onClick='followLink(event, this, renderRoutesSubset)'>"+item.location+"</a>";
    }
    if (item.discipline !== undefined) {
      var value = "<a href='" +
                  item["@controls"]["disciplines:in-discipline"].href +
                  "' onClick='followLink(event, this, renderRoutesSubset)'>"+item.discipline+"</a>";
    }
    if (item.grade !== undefined) {
      var value = "<a href='" +
                  item["@controls"]["grades:in-grade"].href +
                  "' onClick='followLink(event, this, renderRoutesSubset)'>"+item.grade+"</a>";
    }
    return "<tr><td>" + value + "</td></tr>";
}


// get the body of a new submitted user
function getSubmittedUser(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appenduserRow);
    }
}


// append the submitted used to list
function appenduserRow(body) {
    $(".resulttable tbody").append(userRow(body));
}


// get the body of a new submitted route
function getSubmittedRoute(data, status, jqxhr) {
    renderMsg("Successful");
    let href = jqxhr.getResponseHeader("Location");
    if (href) {
        getResource(href, appendRouteRow);
    }
}


// append submitted route to list
function appendRouteRow(body) {
    $(".resulttable tbody").append(routeRow(body));
}


// to follow link relations
function followLink(event, a, renderer) {
    event.preventDefault();
    getResource($(a).attr("href"), renderer);
}


// function to add new user to the DB
function submitUser(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.email = $("input[name='email']").val();
    data.firstName = $("input[name='firstName']").val();
    data.lastName = $("input[name='lastName']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedUser);
}


// function to add new route to the DB
function submitRoute(event) {
    event.preventDefault();

    let data = {};
    let form = $("div.form form");
    data.date = $("input[name='date']").val();
    data.location = $("input[name='location']").val();
    data.discipline = $("input[name='discipline']").val();
    data.grade = $("input[name='grade']").val();
    data.extraInfo = $("input[name='extraInfo']").val();
    sendData(form.attr("action"), form.attr("method"), data, getSubmittedRoute);
}


// function to handle user deletion, takes back to "login" site
function renderUserDelete(body) {
    var answer;
    if (confirm("Do you want to delete user?") == true) {
      answer = "User deleted.";
      let deleteUrl = body["@controls"]["users:delete"].href;
      $.ajax({
           url : deleteUrl,
           method : 'delete',
           success: alert("User has been deleted. You will return to main page")
      })
      location.reload();
    } else {
      answer = "Operation cancelled.";
    }
}


// function to show the items for adding a new user to the DB or editing existing
function renderUserForm(ctrl, msg) {
    let form = $("<form>");
    let email = ctrl.schema.properties.email;
    let firstName = ctrl.schema.properties.firstName;
    let lastName = ctrl.schema.properties.lastName;

    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitUser);
    form.append(msg);
    form.append("<label>" + email.description + "</label>");
    form.append("<input type='text' name='email'>");
    form.append("<label>" + firstName.description + "</label>");
    form.append("<input type='text' name='firstName'>");
    form.append("<label>" + lastName.description + "</label>");
    form.append("<input type='text' name='lastName'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<br> <br> <input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}


// function to handle route deletion
// NOTE: here async functionality is used so that the function "waits" until
// the delete has gone through --> this was the only way I was able to get
// the list to update properly (i.e. in such a way that it does not include still
// the deleted route)
async function renderRouteDelete(body) {
  var answer;
  if (confirm("Do you want to delete route?") == true) {
    answer = "Route deleted.";
    let deleteUrl = body["@controls"]["routes:delete"].href;
    await $.ajax({
            url: deleteUrl,
            method: 'delete',
            success: alert("Route has been deleted.")
            })
    getResource(body["@controls"]["routes:routes-all"].href, renderAllRoutes);
  } else {
    answer = "Operation cancelled.";
  }
}


// function to show the items for adding a new route to the DB, or editing existing
function renderRouteForm(ctrl, msg) {
    let form = $("<form>");
    let date = ctrl.schema.properties.date;
    let location = ctrl.schema.properties.location;
    let discipline = ctrl.schema.properties.discipline;
    let grade = ctrl.schema.properties.grade;
    let extraInfo = ctrl.schema.properties.extraInfo;

    form.attr("action", ctrl.href);
    form.attr("method", ctrl.method);
    form.submit(submitRoute);
    form.append(msg);
    form.append("<label>" + date.description + "</label>");
    form.append("<input type='text' name='date'>");
    form.append("<label>" + location.description + "</label>");
    form.append("<input type='text' name='location'>");
    form.append("<label>" + discipline.description + "</label>");
    form.append("<input type='text' name='discipline'>");
    form.append("<label>" + grade.description + "</label>");
    form.append("<input type='text' name='grade'>");
    form.append("<label>" + extraInfo.description + "</label>");
    form.append("<input type='text' name='extraInfo'>");
    ctrl.schema.required.forEach(function (property) {
        $("input[name='" + property + "']").attr("required", true);
    });
    form.append("<br> <br> <input type='submit' name='submit' value='Submit'>");
    $("div.form").html(form);
}


// route edit form.
// NOTE: this is rather reduced functionality and user has to manually enter route list
// again after edit.
function renderRouteEdit(body) {
  $("div.textheader").html(
    "<h1> Routetracker development user site </h1>"
  );
  $("div.textbox").html(`This page contains single route editing and deletion. <br>
  You can choose to go back to the user information, the route list, or edit the route information. <br> <br>
  <p style="color:red"> Current implementation requires that the user clicks back to "all routes", "locations",
  "disciplines", or "grades" after edit, it does not redirect automatically. </p>`
  );

    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();

    //Edit user information:
    $("div.form").empty();
    renderRouteForm(body["@controls"]["routes:edit-route"], "<br> <br> <h2>Edit route information:</h2> <br>");
    $("input[name='date']").val(body.date);
    $("input[name='location']").val(body.location);
    $("input[name='discipline']").val(body.discipline);
    $("input[name='grade']").val(body.grade);
    $("input[name='extraInfo']").val(body.extraInfo);
    $("<br> <br> form input[type='submit']").before(
        "<label>Location</label>" +
        "<input type='text' name='location' value='" +
        body.location + "' readonly>"
    );
}


// for displaying main route categories user has done (locations, disciplines, grades)
function renderRouteValues(body) {
    $("div.textbox").html(`This page contains routes main values in either location, discipline, or grade subsets. <br>
      You can choose to go back to user information, list of all routes, or further explore routes under specific value.`
    );
    $("div.navigation").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["users:climbed-by"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderUser)'>user</a> | " +
        "<a href='" +
        body["@controls"]["routes:routes-all"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderAllRoutes)'>all routes</a>"
    );

    let tablectrl = $("div.tablecontrols");
    tablectrl.empty();
    $(".resulttable thead").html(
        "<tr> <th>Item</th> </tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(routeItemRow(item));
    });
    $("div.form").empty();
}


// for showing specific subset of routes
function renderRoutesSubset(body) {
    if (body["@controls"]["locations:locations-all"] !== undefined) {
      var back = "<a href='" +
              body["@controls"]["locations:locations-all"].href.replace("{index}", "0") +
              "' onClick='followLink(event, this, renderRouteValues)'>all locations</a>"
    }
    if (body["@controls"]["disciplines:disciplines-all"] !== undefined) {
      var back = "<a href='" +
              body["@controls"]["disciplines:disciplines-all"].href.replace("{index}", "0") +
              "' onClick='followLink(event, this, renderRouteValues)'>all disciplines</a>"
    }
    if (body["@controls"]["grades:grades-all"] !== undefined) {
      var back = "<a href='" +
              body["@controls"]["grades:grades-all"].href.replace("{index}", "0") +
              "' onClick='followLink(event, this, renderRouteValues)'>all grades</a>"
    }


    $("div.textbox").html(`This page contains routes in specific subset. <br>
      You can choose to go back to user information, list of all routes, or to parent of this subset. `
    );
    $("div.navigation").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["users:climbed-by"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderUser)'>user</a> | " +
        "<a href='" +
        body["@controls"]["routes:routes-all"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderAllRoutes)'>all routes</a> | " +
        back
    );
    let tablectrl = $("div.tablecontrols");
    tablectrl.empty();
    $(".resulttable thead").html(
        "<tr> <th>Date</th> <th>Location</th> <th>Discipline</th> <th>Grade</th> <th>Information</th> <th> </th> <th> </th> </tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(routeRowSubset(item));
    });
    $("div.form").empty();
}


// route list page for user, has also the ability to add a new route
function renderAllRoutes(body) {
    $("div.textbox").html(`This page contains routes main controls. <br>
      You can choose to go back to user information, or look at the locations, disciplines, and grades of the climbed routes. <br>
      Each link in the table also takes to list of routes in that specific value. <br> <br>
      For the time being, individual routes can be added, edited, and deleted only in this page.`
    );
    $("div.navigation").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["users:climbed-by"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderUser)'>user</a> | " +
        "<a href='" +
        body["@controls"]["routes:routes-all"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderAllRoutes)'>all routes</a> | " +
        "<a href='" +
        body["@controls"]["locations:locations-all"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderRouteValues)'>locations</a> | " +
        "<a href='" +
        body["@controls"]["disciplines:disciplines-all"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderRouteValues)'>disciplines</a> | " +
        "<a href='" +
        body["@controls"]["grades:grades-all"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderRouteValues)'>grades</a>"
    );
    let tablectrl = $("div.tablecontrols");
    tablectrl.empty();
    $(".resulttable thead").html(
        "<tr> <th>Date</th> <th>Location</th> <th>Discipline</th> <th>Grade</th> <th>Information</th>  <th> </th> <th> </th> </tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(routeRow(item));
    });
    $("div.form").empty();
    renderRouteForm(body["@controls"]["routes:add-route"], "<br> <br> <h2>Add a new route:</h2> <br>");
}


// render the entry page for user after "login"
function renderUser(body) {
  $("div.textbox").html(`This page contains user main controls. <br>
  You can choose to go back to main entry site (logout), look at the routes user has, or edit or delete the user. `
  );
    $("div.navigation").empty();
    $("div.navigation").html(
        "<a href='" +
        body["@controls"]["users:users-all"].href +
        "' onClick='followLink(event, this, renderUsers)'>Logout</a> | " +
        "<a href='" +
        body["@controls"]["routes:routes-all"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderAllRoutes)'>routes</a>  | " +
        "<a href='" +
        body["@controls"]["users:delete"].href.replace("{index}", "0") +
        "' onClick='followLink(event, this, renderUserDelete)'>delete user</a>"
    );
    $(".resulttable thead").empty();
    $(".resulttable tbody").empty();

    //Edit user information:
    renderUserForm(body["@controls"]["users:edit-user"], "<br> <br> <h2>Edit user information:</h2> <br>");
    $("input[name='email']").val(body.email);
    $("input[name='firstName']").val(body.firstName);
    $("input[name='lastName']").val(body.lastName);
    $("<br> <br> form input[type='submit']").before(
        "<label>Location</label>" +
        "<input type='text' name='location' value='" +
        body.location + "' readonly>"
    );
}


// "login" page: shows in this development version the list of users and gives links to access them.
// has also a form to add a new user.
function renderUsers(body) {
    $("div.textheader").html(
      "<h1> Routetracker development client </h1>"
    );
    $("div.textbox").html(`This page would contain login. <br>
    Now you can choose to show one existing user with climbed routes, or create a new user without any routes,
    to explore rest of the functionality.`
    );

    $("div.navigation").empty();
    $("div.tablecontrols").empty();
    $(".resulttable thead").html(
        "<br> <tr><th>Email</th><th>First name</th><th>Last name</th><th>Actions</th></tr>"
    );
    let tbody = $(".resulttable tbody");
    tbody.empty();
    body.items.forEach(function (item) {
        tbody.append(userRow(item));
    });
    renderUserForm(body["@controls"]["users:add-user"], "<br> <br> <h2>Add a new user to the DB:</h2> <br>");
}


// entry point to the api: GET the users list and point to first page.
$(document).ready(function () {
    getResource("http://localhost:5000/api/users/", renderUsers);
});
