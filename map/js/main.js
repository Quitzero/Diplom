//-----------------------| Карта |----------------------------------------------
// Создание опций карты
var mapOptions = {
    center: [60.8823, 68.9831],
    
    maxZoom: 14,
    minZoom: 5,
    zoom: 8,
    maxBounds: [
        //south west
        [57.4212, 56.4257],
        //north east
        [66.4079, 87.4951]
        ], 

}
 
// Создание объекта карты
var map = new L.map('map', mapOptions);
 
// Создание объекта слоя
var layer = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png');
map.attributionControl.addAttribution('&copy; OpenStreetMap</a>');

// Добавление слоя на карту
map.addLayer(layer);


//-----------------------| Панель инструментов |----------------------------------------------
// FeatureGroup предназначена для хранения редактируемых объектов
var drawnFeatures = new L.FeatureGroup();
map.addLayer(drawnFeatures);

// Создание опций панели инструментов
var options = {
    position: 'topleft',
    draw: {
        marker: false,
        circle: false,
        polyline: false,
        circlemarker: false,
    },
}

// Создание объекта панели инструментов
var drawControl = new L.Control.Draw(options);
map.addControl(drawControl);



//-----------------------| Функционал панели инструментов |----------------------------------------------
// Создаение объекта QWebChannel и функции передающей данные в app.py 
var backend = null;
function showCoords(coords) {
    new QWebChannel(qt.webChannelTransport, function(channel) {
        backend = channel.objects.backend;
        backend.getRef(coords);
    });
}

var poly = []

function addPoly(a, b, c, d) {
    poly.push(L.polygon([a, b, c, d]))
}

function renderPoly(index) {
    poly[index].addTo(map);
}

function clear() {
    for (let i = 0; i <= poly.length-1; i++) {
        poly[i].remove(map)
        poly.slice(i, 1)
    }
    poly = []
}


function redraw(p){
    var polygon = drawnFeatures.getLayers()[0];
    polygon.setLatLngs(p);
    drawnFeatures.redraw;
}

// Вызов функции showCoords при создании объекта и его добавление в FeatureGroup
map.on('draw:created', function (e){
    var layer = e.layer;
    if(drawnFeatures && drawnFeatures.getLayers().length!==0){
        drawnFeatures.clearLayers();
    }
    drawnFeatures.addLayer(layer);
    showCoords(layer.getLatLngs())
});
    

// Запись координат в консоль при изменении объекта
map.on('draw:edited', function (e) {
    var layers = e.layers;
    layers.eachLayer(function (layer) {
        showCoords(layer.getLatLngs())
    });
});


map.on('draw:deleted', function (e) {
    var layers = e.layers;
    layers.eachLayer(function (layer) {
        deleteCoords()
    });
});



