{% if settings.SITE.plugins.beid.urlhandler_prefix %}

function uuid() {
  // Copied from https://gist.github.com/jcxplorer/823878
  var uuid = "", i, random;
  for (i = 0; i < 32; i++) {
    random = Math.random() * 16 | 0;

    if (i == 8 || i == 12 || i == 16 || i == 20) {
      uuid += "-"
    }
    uuid += (i == 12 ? 4 : (i == 16 ? (random & 3 | 8) : random)).toString(16);
  }
  return uuid;
};

Lino.beid_read_card_processor = function() {
    // var card = {}
    var my_id = uuid();
    var url = "{{settings.SITE.plugins.beid.urlhandler_prefix}}" + window.location.origin + "/eid/" + my_id;
    // var current_window = window.window;
    console.log("Gonna open", url);
    var popup = window.open(url, "eidreader");
    // while (popup.event) {setTimeout(()=>console.log("waiting", popup.event),1000)};
    // popup.close();
    // current_window.focus();
    return { uuid: my_id, timeout: {{settings.SITE.plugins.beid.preprocessor_delay}} };

    // var xhttp = new XMLHttpRequest();
    // xhttp.onreadystatechange = function() {
    //     if (this.readyState == 4 && this.status == 200) {
    //         card = JSON.parse(this.responseText);
    //     } else {
    //         console.log("20180412 status ", this.status);
    //     }
    // };
    // xhttp.open("GET", "/eid/" + my_id, false);
    // xhttp.send();

    // return { card_data: card };
}

{% else %}

Lino.beid_read_card_processor = function() {
    var card = document.applets.EIDReader.readCard();
    // if (!card) {
    //     Lino.alert("Could not find any card on your reader.");
    //     return null;
    // }
    // console.log(20140301, card);
    return { card_data: card };
}

{% endif %}
