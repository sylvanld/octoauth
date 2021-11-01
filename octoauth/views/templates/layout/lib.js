const XHR_DONE = 4;

function buildQueryString(query){
    if(query === undefined || Object.keys(query).length === 0) return null;
    return Object.keys(query).map(param=>[param, encodeURIComponent(query[param])].join("=")).join("&");
}

function parseFormData(formElement){
    let data = {};
    for(let [key, value] of new FormData(formElement).entries()){
        data[key] = value
    };
    return data;
}

function request(method, uri, {json, form, query}){
    const queryString = buildQueryString(query);
    let requestBody = null;
    
    const xhr = new XMLHttpRequest();
    xhr.open(method, uri + (queryString === null ? "": "?" + queryString));

    if(json !== undefined){
        xhr.setRequestHeader("Content-Type", "application/json");
        requestBody = JSON.stringify(json);
    }else if(form !== undefined){
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        requestBody = buildQueryString(form);
    }

    return new Promise((resolve, reject)=>{
        xhr.onreadystatechange = ()=>{
            if(xhr.readyState === XHR_DONE){
                // by default, assume data is JSON, otherwise, use raw text
                try{
                    data = JSON.parse(xhr.responseText);
                }catch{
                    data = xhr.responseText;
                }
                resolve({data, status: xhr.status});
            }
        }
        xhr.send(requestBody);
    })
}

class requests{
    static get(uri, query){
        return request("GET", uri, {query});
    }

    static post(uri, {json, form}){
        return request('POST', uri, {json, form});
    }
}

//
const $ = (s) =>document.querySelector("#" + s);

function clearErrors(){
    let displayError = $("errorMessage");
    displayError.innerText = "";
    displayError.style.display = "none";

    document.querySelectorAll("fieldset")
    .forEach(fieldset=>fieldset.classList.remove("error"));
}

function showFieldsError(message, ...fieldsets){
    let displayError = $("errorMessage");
    displayError.innerText = message;
    displayError.style.display = "block";

    console.log(fieldsets);

    fieldsets.forEach(fieldset => fieldset.classList.add("error"));
}
