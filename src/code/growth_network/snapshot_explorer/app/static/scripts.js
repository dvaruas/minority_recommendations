var nodes = new vis.DataSet({});
var edges = new vis.DataSet({});
var network = null;
var curr_t = 0;
var intVal = null;
var minority_count = 0;
var majority_count = 0;
var paused = false;

function updateMinMajCount(min_change, maj_change, remove) {
  if (remove) {
    minority_count -= min_change;
    majority_count -= maj_change;
  } else {
    minority_count += min_change;
    majority_count += maj_change;
  }
  let actual_frac = Math.round((minority_count / majority_count) * 100) / 100;
  $("#min_count").text(`Minority : ${minority_count}`);
  $("#maj_count").text(`Majority : ${majority_count}`);
  $("#actual_mf").text(`${actual_frac}`);
}

function dealWithResult(result, remove) {
  document.getElementById("changeLog").innerHTML = `<li>Iteration : ${curr_t}</li>`;
  $(result["events"]).each(function(_, v) {
    document.getElementById("changeLog").innerHTML += `<li>${v}</li>`;
  });
  $(result["network"]).each(function(_, v) {
    if (v.hasOwnProperty("id")) {
      // This is a new node added
      if (remove) nodes.remove(v["id"]);
      else nodes.add(v);
      if (network) network.stabilize();
    } else if (v.hasOwnProperty("from")) {
      // This is a new edge
      if (remove) edges.remove(v);
      else edges.add(v);
    }
  });
  updateMinMajCount(result["min_change"], result["maj_change"], remove);
  if (network == null) {
    var data = {
      nodes: nodes,
      edges: edges,
    };
    var options = {};
    var container = document.getElementById("canvas");
    network = new vis.Network(container, data, options);
  }
}

$("#runButton").click(function() {
  if (paused == false && network) {
    network.destroy();
    network = null;
    nodes.clear();
    edges.clear();
  }
  var t0 = 0;
  if (paused) t0 = curr_t;
  let interval = $("#viewTime").val();

  paused = false;
  intVal = setInterval(function() {
    $.ajax({
      type : "GET",
      url : `/get_next?t0=${t0}&t=${t0+1}`,
      dataType : "json",
      success : function(result) {
        if (result["finished"] == true) {
          clearInterval(intVal);
          $('#forwardButton').prop("disabled", true);
        } else {
          t0 += 1;
          curr_t = t0;
          dealWithResult(result, false);
          if (curr_t > 0) $('#backButton').prop("disabled", false);
        }
      },
      error: function (xhr, ajaxOptions, thrownError) {
        clearInterval(intVal);
        intVal = null;
      }
    });
  }, (interval * 1000));
});

$("#pauseButton").click(function() {
  if (intVal) {
    clearInterval(intVal);
    intVal = null;
  }
  paused = true;
});

$("#backButton").click(function() {
  if ($('#backButton').prop("disabled") == false) {
    $.ajax({
      type : "GET",
      url : `/get_next?t0=${curr_t}&t=${curr_t - 1}`,
      dataType : "json",
      success : function(result) {
        if (result["finished"] == true) {
          $('#backButton').prop("disabled", true);
          document.getElementById("changeLog").innerHTML = '';
        } else {
          curr_t -= 1;
          dealWithResult(result, true);
          if (curr_t <= 0) {
            $('#backButton').prop("disabled", true);
            document.getElementById("changeLog").innerHTML = '';
          }
          $('#forwardButton').prop("disabled", false);
        }
      }
    });
  }
});

$("#forwardButton").click(function() {
  if ($("#forwardButton").prop("disabled") == false) {
    $.ajax({
      type : "GET",
      url : `/get_next?t0=${curr_t}&t=${curr_t + 1}`,
      dataType : "json",
      success : function(result) {
        if (result["finished"] == true) $('#forwardButton').prop("disabled", true);
        else {
          curr_t += 1;
          dealWithResult(result, false);
          if (curr_t > 0) $('#backButton').prop("disabled", false);
        }
      }
    });
  }
});

$("#resetButton").click(function() {
  if (intVal) {
    clearInterval(intVal);
    intVal = null;
  }
  if (network) {
    network.destroy();
    network = null;
    nodes.clear();
    edges.clear();
  }
  curr_t = 0;
  paused = false;
  document.getElementById("changeLog").innerHTML = '';
  updateMinMajCount(minority_count, majority_count, true);
  $('#backButton').prop("disabled", true);
});
