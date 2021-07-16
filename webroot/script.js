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
