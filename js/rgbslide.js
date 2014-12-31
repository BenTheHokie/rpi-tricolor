$('#rs').slider(
    {
	formater: function(value) {
	    return 'Red: ' + value;
	}
    }
);
$('#gs').slider(
    {
	formater: function(value) {
	    return 'Green: ' + value;
	}
    }
);
$('#bs').slider(
    {
	formater: function(value) {
	    return 'Blue: ' + value;
	}
    }
);

var rgb = { r : 50, g : 50, b : 50};
var rgbp = { r : 50, g : 50, b : 50}; // rgb previous values

$('#rs').on('slide', function(d) 
    {
	rgb.r = Number(d.value);
	if( Math.abs(rgb.r - rgbp.r) >= 5) {
	    rgbp.r = rgb.r;
	    socket.send( JSON.stringify(rgb) );
	}
    }
);
$('#gs').on('slide', function(d) 
    {
	rgb.g = Number(d.value);
	if( Math.abs(rgb.g - rgbp.g) >= 5) {
	    rgbp.g = rgb.g;
	    socket.send( JSON.stringify(rgb) );
	}
    }
);
$('#bs').on('slide', function(d) 
    {
	rgb.b = Number(d.value);
	if( Math.abs(rgb.b - rgbp.b) >= 5) {
	    rgbp.b = rgb.b;
	    console.log('sent: '+JSON.stringify(rgb));
	    socket.send( JSON.stringify(rgb) );
	}
    }
);


var dragging = false;
$('.slider').on('mousedown', function(){dragging = true;});
$(document.body).on('mouseup',function(){
    if(dragging){
	dragging=false;
	console.log('Dragged!');
	rgbp.r = rgb.r; rgbp.g = rgb.g; rgbp.b = rgb.b;
	console.log('sent: '+JSON.stringify(rgb));
	socket.send( JSON.stringify(rgb) );
    }
});
