function search(value)
{
    var search_terms = value.split(" ")
    var index_elements = document.querySelectorAll('[id^=index_element]');
    console.log(index_elements)
    index_elements.forEach(element => {
        matches = true
        search_terms.forEach(term => {
            if(element.innerHTML.toUpperCase().indexOf(term.toUpperCase()) == -1)
            {
                matches = false;
            }
        });

        if(matches)
        {
            element.style.display = "";
        }
        else{
            element.style.display = "none";
        }
    });
}

function full_text_search()
{
    referer_url = "https://zealous-river-0de318e03.azurestaticapps.net"
    api_url = "https://fulltextsearch.norwayeast.azurecontainer.io"
    search_term = document.getElementById("full-text-search-input").value;
    console.log("Got here")
    //headers = {"ContentType": "text/html"}
    api_url_formatted = api_url+"?search_str="+search_term+"&referer_url="+referer_url
    //response = requests.post(url = api_url, headers=headers)
    fetch(api_url_formatted).then( function(response) {
        console.log(response)
        response.text().then(function(text) {
            var search_results_div = document.getElementById('full_text_search_results');
            search_results_div.innerHTML = text;
        });
    });
}
