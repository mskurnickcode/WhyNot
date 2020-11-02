var clone_count = 0

function insertAfter(referenceNode, newNode) {
  referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}


 function addCountries() {
 		clone_count ++;
 		var list = document.getElementById("country_list");
        var elmnt = document.getElementById("nameList_0");
        var cln = elmnt.cloneNode(true);
        cln.setAttribute('id', 'nameList_'+clone_count);
        cln.setAttribute('name', 'nameList_'+clone_count);
        var newItem = document.createElement("LI")
        newItem.id= "list_item"+clone_count;

        var Currency = document.getElementById("currency_0")
        var newCurrency = Currency.cloneNode(true)
        newCurrency.id = "currency_"+clone_count;
        newCurrency.className = "currency_rate"

		var countryLevel = document.getElementById("countryLevel_0")
		var newCountryLevel = countryLevel.cloneNode(true)
		newCountryLevel.id = "countryLevel_"+clone_count;
		newCountryLevel.className = "link";

		var linebreak = document.createElement("br")
        list.appendChild(newItem);
		insertAfter(newItem, cln);
		insertAfter(cln, newCurrency);
		insertAfter(newCurrency, linebreak)
		insertAfter(linebreak, newCountryLevel);

    }

//query api for currency data
function getExchangeRates(currency) {

var request = new XMLHttpRequest()
var currencySelector= document.getElementById("currency");
var currency=currencySelector.options[currencySelector.selectedIndex].value;

if (currency === "initial") {
	return;
}
request.open('GET', 'https://api.exchangeratesapi.io/latest?base='+currency, true)
request.onload = function () {
  // Begin accessing JSON data here
  var data = JSON.parse(this.response)

  if (request.status >= 200 && request.status < 400) {
      var currency = document.getElementsByClassName("currency_rate");

      for (var i=0; i <= currency.length; i++) {
        var selectedName = document.getElementById("nameList_"+i).value;
        var concated = selectedName.substring(selectedName.length - 3, selectedName.length);

        if(data.rates[concated] === undefined){
          currency[i].innerHTML = "Currency Unavailable"
        } else {
          currency[i].innerHTML = data.rates[concated];
        }

      //for (var j = 0, j)
      //if(concated ===
      console.log(data.rates[concated]);
    }
      //for(var i = 0, i <= clone_count, i++){
      //}

  } else {
    console.log('error')
    alert("Issue fetching currency rates currently")
  }
}

request.send();
}

function tripName () {
  button = document.getElementById("save");
  input = document.getElementById("trip_name");
  links = document.getElementsByClassName("link")

  if (input.value === "") {
    button.disabled = true;
    links.disabled = true;
  } else {
    button.disabled = false;
    links.disabled = false;
  }
}

window.oninput = tripName

function htmlUpdate () {
  links = document.getElementsByClassName("link")
  input = document.getElementById("trip_name");

   if (input.value !== "") {
      for (var i=0; i <= clone_count; i++) {
        var country_link = document.getElementById("countryLevel_"+i)
        var selector= document.getElementById("nameList_"+i);
        var selected=selector.options[selector.selectedIndex].value;
        var trip_name = document.getElementById("trip_name").value;

        country_link.setAttribute("href",'/'+trip_name+'/'+selected);
        console.log(country_link);
  }
}


}

window.onchange = htmlUpdate