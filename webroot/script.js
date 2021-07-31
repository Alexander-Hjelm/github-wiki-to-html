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

function full_text_search(value)
{
    referer_url = "https://zealous-river-0de318e03.azurestaticapps.net"
    api_url = "http://fulltextsearch.norwayeast.azurecontainer.io"
    search_term = value
    console.log("Got here")
    var search_results_div = document.getElementById('[id^=full_text_search_results]');
    headers = {"ContentType": "text/html"}
    api_url_formatted = "{0}?search_str={1}&eferer_url={2}".format(api_url, search_term, referer_url)
    response = requests.post(url = api_url, headers=headers)
    console.log(response)
    search_results_div.innerHTML = response
}
