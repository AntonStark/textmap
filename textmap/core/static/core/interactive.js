const backendUrl = 'http://localhost:8000/textmap/';

console.log('script loaded');

function scrollHandler(e) {
    console.log('start scrollHandler', e)
}
// window.addEventListener('scroll', scrollHandler);

/*
* maybe_todo Обработчик скрола следит за актуальностью глобальной ссылки на первый хотя бы частично видимый абзац
* */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

function sBS() {
    let req = new XMLHttpRequest();
    // req.open('POST', backendUrl + 'text/38e983c6-aee7-47c8-99c7-a7febfd84e57/action/');
    req.open('POST', '/textmap/text/38e983c6-aee7-47c8-99c7-a7febfd84e57/action/');
    req.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    req.setRequestHeader('X-CSRFToken', csrftoken);
    req.onreadystatechange = function () {
        if (this.readyState === 4) {
            const res = JSON.parse(this.responseText);
            console.log(this.status, res);
        }
        else {
            console.log(this.readyState);
        }
    };

    const eventBody = {
        'from_paragraph': 'a261a3c4-355a-46fe-adec-b5614f44379e',
        'to_paragraph': '02596bcc-2fef-4f6c-ae20-41b6d0f2242e'
    };
    console.log('sending request....');
    req.send(JSON.stringify({
        'type': 'BUILD_SECTION',
        'body': eventBody
    }));
}
