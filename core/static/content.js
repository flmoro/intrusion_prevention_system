$(document).ready(function changeColor() {
    // connect to the server
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/dep');

    // receive details from server
    socket.on('detect', function(msg) {
        if (msg['anomalous_flows'] > 0){
            $('#anomalies').html(msg['anomalous_flows']).css('color', 'red');
        }
    });
});

function hiddenForm() {
    var p = document.createElement('p')
    var text = document.createTextNode('Loading...');

    p.appendChild(text);
    document.querySelector('main').appendChild(p);
    document.getElementById('loading').style.display = 'none';
};
