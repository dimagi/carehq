/*
 * Pixastic - JavaScript Image Processing Library
 * Copyright (c) 2008 Jacob Seidelin, jseidelin@nihilogic.dk, http://blog.nihilogic.dk/
 * MIT License [http://www.pixastic.com/lib/license.txt]
 */


var Pixastic=(function(){function addEvent(el,event,handler){if(el.addEventListener)
el.addEventListener(event,handler,false);else if(el.attachEvent)
el.attachEvent("on"+event,handler);}
function onready(handler){var handlerDone=false;var execHandler=function(){if(!handlerDone){handlerDone=true;handler();}}
document.write("<"+"script defer src=\"//:\" id=\"__onload_ie_pixastic__\"></"+"script>");var script=document.getElementById("__onload_ie_pixastic__");script.onreadystatechange=function(){if(script.readyState=="complete"){script.parentNode.removeChild(script);execHandler();}}
if(document.addEventListener)
document.addEventListener("DOMContentLoaded",execHandler,false);addEvent(window,"load",execHandler);}
function init(){var imgEls=getElementsByClass("pixastic",null,"img");var canvasEls=getElementsByClass("pixastic",null,"canvas");var elements=imgEls.concat(canvasEls);for(var i=0;i<elements.length;i++){(function(){var el=elements[i];var actions=[];var classes=el.className.split(" ");for(var c=0;c<classes.length;c++){var cls=classes[c];if(cls.substring(0,9)=="pixastic-"){var actionName=cls.substring(9);if(actionName!="")
actions.push(actionName);}}
if(actions.length){if(el.tagName.toLowerCase()=="img"){var dataImg=new Image();dataImg.src=el.src;if(dataImg.complete){for(var a=0;a<actions.length;a++){var res=Pixastic.applyAction(el,el,actions[a],null);if(res)
el=res;}}else{dataImg.onload=function(){for(var a=0;a<actions.length;a++){var res=Pixastic.applyAction(el,el,actions[a],null)
if(res)
el=res;}}}}else{setTimeout(function(){for(var a=0;a<actions.length;a++){var res=Pixastic.applyAction(el,el,actions[a],null);if(res)
el=res;}},1);}}})();}}
if(typeof pixastic_parseonload!="undefined"&&pixastic_parseonload)
onready(init);function getElementsByClass(searchClass,node,tag){var classElements=new Array();if(node==null)
node=document;if(tag==null)
tag='*';var els=node.getElementsByTagName(tag);var elsLen=els.length;var pattern=new RegExp("(^|\\s)"+searchClass+"(\\s|$)");for(i=0,j=0;i<elsLen;i++){if(pattern.test(els[i].className)){classElements[j]=els[i];j++;}}
return classElements;}
var debugElement;function writeDebug(text,level){if(!Pixastic.debug)return;try{switch(level){case"warn":console.warn("Pixastic:",text);break;case"error":console.error("Pixastic:",text);break;default:console.log("Pixastic:",text);}}catch(e){}
if(!debugElement){}}
var hasCanvas=(function(){var c=document.createElement("canvas");var val=false;try{val=!!((typeof c.getContext=="function")&&c.getContext("2d"));}catch(e){}
return function(){return val;}})();var hasCanvasImageData=(function(){var c=document.createElement("canvas");var val=false;var ctx;try{if(typeof c.getContext=="function"&&(ctx=c.getContext("2d"))){val=(typeof ctx.getImageData=="function");}}catch(e){}
return function(){return val;}})();var hasGlobalAlpha=(function(){var hasAlpha=false;var red=document.createElement("canvas");if(hasCanvas()&&hasCanvasImageData()){red.width=red.height=1;var redctx=red.getContext("2d");redctx.fillStyle="rgb(255,0,0)";redctx.fillRect(0,0,1,1);var blue=document.createElement("canvas");blue.width=blue.height=1;var bluectx=blue.getContext("2d");bluectx.fillStyle="rgb(0,0,255)";bluectx.fillRect(0,0,1,1);redctx.globalAlpha=0.5;redctx.drawImage(blue,0,0);var reddata=redctx.getImageData(0,0,1,1).data;hasAlpha=(reddata[2]!=255);}
return function(){return hasAlpha;}})();return{parseOnLoad:false,debug:false,applyAction:function(img,dataImg,actionName,options){options=options||{};var imageIsCanvas=(img.tagName.toLowerCase()=="canvas");if(imageIsCanvas&&Pixastic.Client.isIE()){if(Pixastic.debug)writeDebug("Tried to process a canvas element but browser is IE.");return false;}
var canvas,ctx;var hasOutputCanvas=false;if(Pixastic.Client.hasCanvas()){hasOutputCanvas=!!options.resultCanvas;canvas=options.resultCanvas||document.createElement("canvas");ctx=canvas.getContext("2d");}
var w=img.offsetWidth;var h=img.offsetHeight;if(imageIsCanvas){w=img.width;h=img.height;}
if(w==0||h==0){if(img.parentNode==null){var oldpos=img.style.position;var oldleft=img.style.left;img.style.position="absolute";img.style.left="-9999px";document.body.appendChild(img);w=img.offsetWidth;h=img.offsetHeight;document.body.removeChild(img);img.style.position=oldpos;img.style.left=oldleft;}else{if(Pixastic.debug)writeDebug("Image has 0 width and/or height.");return;}}
if(actionName.indexOf("(")>-1){var tmp=actionName;actionName=tmp.substr(0,tmp.indexOf("("));var arg=tmp.match(/\((.*?)\)/);if(arg[1]){arg=arg[1].split(";");for(var a=0;a<arg.length;a++){thisArg=arg[a].split("=");if(thisArg.length==2){if(thisArg[0]=="rect"){var rectVal=thisArg[1].split(",");options[thisArg[0]]={left:parseInt(rectVal[0],10)||0,top:parseInt(rectVal[1],10)||0,width:parseInt(rectVal[2],10)||0,height:parseInt(rectVal[3],10)||0}}else{options[thisArg[0]]=thisArg[1];}}}}}
if(!options.rect){options.rect={left:0,top:0,width:w,height:h};}else{options.rect.left=Math.round(options.rect.left);options.rect.top=Math.round(options.rect.top);options.rect.width=Math.round(options.rect.width);options.rect.height=Math.round(options.rect.height);}
var validAction=false;if(Pixastic.Actions[actionName]&&typeof Pixastic.Actions[actionName].process=="function"){validAction=true;}
if(!validAction){if(Pixastic.debug)writeDebug("Invalid action \""+actionName+"\". Maybe file not included?");return false;}
if(!Pixastic.Actions[actionName].checkSupport()){if(Pixastic.debug)writeDebug("Action \""+actionName+"\" not supported by this browser.");return false;}
if(Pixastic.Client.hasCanvas()){if(canvas!==img){canvas.width=w;canvas.height=h;}
if(!hasOutputCanvas){canvas.style.width=w+"px";canvas.style.height=h+"px";}
ctx.drawImage(dataImg,0,0,w,h);if(!img.__pixastic_org_image){canvas.__pixastic_org_image=img;canvas.__pixastic_org_width=w;canvas.__pixastic_org_height=h;}else{canvas.__pixastic_org_image=img.__pixastic_org_image;canvas.__pixastic_org_width=img.__pixastic_org_width;canvas.__pixastic_org_height=img.__pixastic_org_height;}}else if(Pixastic.Client.isIE()&&typeof img.__pixastic_org_style=="undefined"){img.__pixastic_org_style=img.style.cssText;}
var params={image:img,canvas:canvas,width:w,height:h,useData:true,options:options}
var res=Pixastic.Actions[actionName].process(params);if(!res){return false;}
if(Pixastic.Client.hasCanvas()){if(params.useData){if(Pixastic.Client.hasCanvasImageData()){canvas.getContext("2d").putImageData(params.canvasData,options.rect.left,options.rect.top);canvas.getContext("2d").fillRect(0,0,0,0);}}
if(!options.leaveDOM){canvas.title=img.title;canvas.imgsrc=img.imgsrc;if(!imageIsCanvas)canvas.alt=img.alt;if(!imageIsCanvas)canvas.imgsrc=img.src;canvas.className=img.className;canvas.style.cssText=img.style.cssText;canvas.name=img.name;canvas.tabIndex=img.tabIndex;canvas.id=img.id;if(img.parentNode&&img.parentNode.replaceChild){img.parentNode.replaceChild(canvas,img);}}
options.resultCanvas=canvas;return canvas;}
return img;},prepareData:function(params,getCopy){var ctx=params.canvas.getContext("2d");var rect=params.options.rect;var dataDesc=ctx.getImageData(rect.left,rect.top,rect.width,rect.height);var data=dataDesc.data;if(!getCopy)params.canvasData=dataDesc;return data;},process:function(img,actionName,options,callback){if(img.tagName.toLowerCase()=="img"){var dataImg=new Image();dataImg.src=img.src;if(dataImg.complete){var res=Pixastic.applyAction(img,dataImg,actionName,options);if(callback)callback(res);return res;}else{dataImg.onload=function(){var res=Pixastic.applyAction(img,dataImg,actionName,options)
if(callback)callback(res);}}}
if(img.tagName.toLowerCase()=="canvas"){var res=Pixastic.applyAction(img,img,actionName,options);if(callback)callback(res);return res;}},revert:function(img){if(Pixastic.Client.hasCanvas()){if(img.tagName.toLowerCase()=="canvas"&&img.__pixastic_org_image){img.width=img.__pixastic_org_width;img.height=img.__pixastic_org_height;img.getContext("2d").drawImage(img.__pixastic_org_image,0,0);if(img.parentNode&&img.parentNode.replaceChild){img.parentNode.replaceChild(img.__pixastic_org_image,img);}
return img;}}else if(Pixastic.Client.isIE()){if(typeof img.__pixastic_org_style!="undefined")
img.style.cssText=img.__pixastic_org_style;}},Client:{hasCanvas:hasCanvas,hasCanvasImageData:hasCanvasImageData,hasGlobalAlpha:hasGlobalAlpha,isIE:function(){return!!document.all&&!!window.attachEvent&&!window.opera;}},Actions:{}}})();Pixastic.Actions.colorhistogram={array256:function(default_value){arr=[];for(var i=0;i<256;i++){arr[i]=default_value;}
return arr},process:function(params){var values=[];if(typeof params.options.returnValue!="object"){params.options.returnValue={rvals:[],gvals:[],bvals:[]};}
var paint=!!(params.options.paint);var returnValue=params.options.returnValue;if(typeof returnValue.values!="array"){returnValue.rvals=[];returnValue.gvals=[];returnValue.bvals=[];}
if(Pixastic.Client.hasCanvasImageData()){var data=Pixastic.prepareData(params);params.useData=false;var rvals=this.array256(0);var gvals=this.array256(0);var bvals=this.array256(0);var rect=params.options.rect;var p=rect.width*rect.height;var pix=p*4;while(p--){rvals[data[pix-=4]]++;gvals[data[pix+1]]++;bvals[data[pix+2]]++;}
returnValue.rvals=rvals;returnValue.gvals=gvals;returnValue.bvals=bvals;if(paint){var ctx=params.canvas.getContext("2d");var vals=[rvals,gvals,bvals];for(var v=0;v<3;v++){var yoff=(v+1)*params.height/3;var maxValue=0;for(var i=0;i<256;i++){if(vals[v][i]>maxValue)
maxValue=vals[v][i];}
var heightScale=params.height/3/maxValue;var widthScale=params.width/256;if(v==0)ctx.fillStyle="rgba(255,0,0,0.5)";else if(v==1)ctx.fillStyle="rgba(0,255,0,0.5)";else if(v==2)ctx.fillStyle="rgba(0,0,255,0.5)";for(var i=0;i<256;i++){ctx.fillRect(i*widthScale,params.height-heightScale*vals[v][i]-params.height+yoff,widthScale,vals[v][i]*heightScale);}}}
return true;}},checkSupport:function(){return Pixastic.Client.hasCanvasImageData();}}
Pixastic.Actions.edges={process:function(params){var mono=!!(params.options.mono&&params.options.mono!="false");var invert=!!(params.options.invert&&params.options.invert!="false");if(Pixastic.Client.hasCanvasImageData()){var data=Pixastic.prepareData(params);var dataCopy=Pixastic.prepareData(params,true)
var c=-1/8;var kernel=[[c,c,c],[c,1,c],[c,c,c]];weight=1/c;var rect=params.options.rect;var w=rect.width;var h=rect.height;var w4=w*4;var y=h;do{var offsetY=(y-1)*w4;var nextY=(y==h)?y-1:y;var prevY=(y==1)?0:y-2;var offsetYPrev=prevY*w*4;var offsetYNext=nextY*w*4;var x=w;do{var offset=offsetY+(x*4-4);var offsetPrev=offsetYPrev+((x==1)?0:x-2)*4;var offsetNext=offsetYNext+((x==w)?x-1:x)*4;var r=((dataCopy[offsetPrev-4]
+dataCopy[offsetPrev]
+dataCopy[offsetPrev+4]
+dataCopy[offset-4]
+dataCopy[offset+4]
+dataCopy[offsetNext-4]
+dataCopy[offsetNext]
+dataCopy[offsetNext+4])*c
+dataCopy[offset])*weight;var g=((dataCopy[offsetPrev-3]
+dataCopy[offsetPrev+1]
+dataCopy[offsetPrev+5]
+dataCopy[offset-3]
+dataCopy[offset+5]
+dataCopy[offsetNext-3]
+dataCopy[offsetNext+1]
+dataCopy[offsetNext+5])*c
+dataCopy[offset+1])*weight;var b=((dataCopy[offsetPrev-2]
+dataCopy[offsetPrev+2]
+dataCopy[offsetPrev+6]
+dataCopy[offset-2]
+dataCopy[offset+6]
+dataCopy[offsetNext-2]
+dataCopy[offsetNext+2]
+dataCopy[offsetNext+6])*c
+dataCopy[offset+2])*weight;if(mono){var brightness=(r*0.3+g*0.59+b*0.11)||0;if(invert)brightness=255-brightness;if(brightness<0)brightness=0;if(brightness>255)brightness=255;r=g=b=brightness;}else{if(invert){r=255-r;g=255-g;b=255-b;}
if(r<0)r=0;if(g<0)g=0;if(b<0)b=0;if(r>255)r=255;if(g>255)g=255;if(b>255)b=255;}
data[offset]=r;data[offset+1]=g;data[offset+2]=b;}while(--x);}while(--y);return true;}},checkSupport:function(){return Pixastic.Client.hasCanvasImageData();}}
Pixastic.Actions.edges2={process:function(params){if(Pixastic.Client.hasCanvasImageData()){var data=Pixastic.prepareData(params);var dataCopy=Pixastic.prepareData(params,true)
var rect=params.options.rect;var w=rect.width;var h=rect.height;var w4=w*4;var pixel=w4+4;var hm1=h-1;var wm1=w-1;for(var y=1;y<hm1;++y){var centerRow=pixel-4;var priorRow=centerRow-w4;var nextRow=centerRow+w4;var r1=-dataCopy[priorRow]-dataCopy[centerRow]-dataCopy[nextRow];var g1=-dataCopy[++priorRow]-dataCopy[++centerRow]-dataCopy[++nextRow];var b1=-dataCopy[++priorRow]-dataCopy[++centerRow]-dataCopy[++nextRow];var rp=dataCopy[priorRow+=2];var gp=dataCopy[++priorRow];var bp=dataCopy[++priorRow];var rc=dataCopy[centerRow+=2];var gc=dataCopy[++centerRow];var bc=dataCopy[++centerRow];var rn=dataCopy[nextRow+=2];var gn=dataCopy[++nextRow];var bn=dataCopy[++nextRow];var r2=-rp-rc-rn;var g2=-gp-gc-gn;var b2=-bp-bc-bn;for(var x=1;x<wm1;++x){centerRow=pixel+4;priorRow=centerRow-w4;nextRow=centerRow+w4;var r=127+r1-rp-(rc*-8)-rn;var g=127+g1-gp-(gc*-8)-gn;var b=127+b1-bp-(bc*-8)-bn;r1=r2;g1=g2;b1=b2;rp=dataCopy[priorRow];gp=dataCopy[++priorRow];bp=dataCopy[++priorRow];rc=dataCopy[centerRow];gc=dataCopy[++centerRow];bc=dataCopy[++centerRow];rn=dataCopy[nextRow];gn=dataCopy[++nextRow];bn=dataCopy[++nextRow];r+=(r2=-rp-rc-rn);g+=(g2=-gp-gc-gn);b+=(b2=-bp-bc-bn);if(r>255)r=255;if(g>255)g=255;if(b>255)b=255;if(r<0)r=0;if(g<0)g=0;if(b<0)b=0;data[pixel]=r;data[++pixel]=g;data[++pixel]=b;pixel+=2;}
pixel+=8;}
return true;}},checkSupport:function(){return Pixastic.Client.hasCanvasImageData();}}
Pixastic.Actions.emboss={process:function(params){var strength=parseFloat(params.options.strength)||1;var greyLevel=typeof params.options.greyLevel!="undefined"?parseInt(params.options.greyLevel):180;var direction=params.options.direction||"topleft";var blend=!!(params.options.blend&&params.options.blend!="false");var dirY=0;var dirX=0;switch(direction){case"topleft":dirY=-1;dirX=-1;break;case"top":dirY=-1;dirX=0;break;case"topright":dirY=-1;dirX=1;break;case"right":dirY=0;dirX=1;break;case"bottomright":dirY=1;dirX=1;break;case"bottom":dirY=1;dirX=0;break;case"bottomleft":dirY=1;dirX=-1;break;case"left":dirY=0;dirX=-1;break;}
if(Pixastic.Client.hasCanvasImageData()){var data=Pixastic.prepareData(params);var dataCopy=Pixastic.prepareData(params,true)
var invertAlpha=!!params.options.invertAlpha;var rect=params.options.rect;var w=rect.width;var h=rect.height;var w4=w*4;var y=h;do{var offsetY=(y-1)*w4;var otherY=dirY;if(y+otherY<1)otherY=0;if(y+otherY>h)otherY=0;var offsetYOther=(y-1+otherY)*w*4;var x=w;do{var offset=offsetY+(x-1)*4;var otherX=dirX;if(x+otherX<1)otherX=0;if(x+otherX>w)otherX=0;var offsetOther=offsetYOther+(x-1+otherX)*4;var dR=dataCopy[offset]-dataCopy[offsetOther];var dG=dataCopy[offset+1]-dataCopy[offsetOther+1];var dB=dataCopy[offset+2]-dataCopy[offsetOther+2];var dif=dR;var absDif=dif>0?dif:-dif;var absG=dG>0?dG:-dG;var absB=dB>0?dB:-dB;if(absG>absDif){dif=dG;}
if(absB>absDif){dif=dB;}
dif*=strength;if(blend){var r=data[offset]+dif;var g=data[offset+1]+dif;var b=data[offset+2]+dif;data[offset]=(r>255)?255:(r<0?0:r);data[offset+1]=(g>255)?255:(g<0?0:g);data[offset+2]=(b>255)?255:(b<0?0:b);}else{var grey=greyLevel-dif;if(grey<0){grey=0;}else if(grey>255){grey=255;}
data[offset]=data[offset+1]=data[offset+2]=grey;}}while(--x);}while(--y);return true;}else if(Pixastic.Client.isIE()){params.image.style.filter+=" progid:DXImageTransform.Microsoft.emboss()";return true;}},checkSupport:function(){return(Pixastic.Client.hasCanvasImageData()||Pixastic.Client.isIE());}}
Pixastic.Actions.histogram={process:function(params){var average=!!(params.options.average&&params.options.average!="false");var paint=!!(params.options.paint&&params.options.paint!="false");var color=params.options.color||"rgba(255,255,255,0.5)";var values=[];if(typeof params.options.returnValue!="object"){params.options.returnValue={values:[]};}
var returnValue=params.options.returnValue;if(typeof returnValue.values!="array"){returnValue.values=[];}
values=returnValue.values;if(Pixastic.Client.hasCanvasImageData()){var data=Pixastic.prepareData(params);params.useData=false;for(var i=0;i<256;i++){values[i]=0;}
var rect=params.options.rect;var p=rect.width*rect.height;var pix=p*4,pix1=pix+1,pix2=pix+2,pix3=pix+3;var round=Math.round;if(average){while(p--){values[round((data[pix-=4]+data[pix+1]+data[pix+2])/3)]++;}}else{while(p--){values[round(data[pix-=4]*0.3+data[pix+1]*0.59+data[pix+2]*0.11)]++;}}
if(paint){var maxValue=0;for(var i=0;i<256;i++){if(values[i]>maxValue){maxValue=values[i];}}
var heightScale=params.height/maxValue;var widthScale=params.width/256;var ctx=params.canvas.getContext("2d");ctx.fillStyle=color;for(var i=0;i<256;i++){ctx.fillRect(i*widthScale,params.height-heightScale*values[i],widthScale,values[i]*heightScale);}}
returnValue.values=values;return true;}},checkSupport:function(){return Pixastic.Client.hasCanvasImageData();}}
Pixastic.Actions.laplace={process:function(params){var strength=1.0;var invert=!!(params.options.invert&&params.options.invert!="false");var contrast=parseFloat(params.options.edgeStrength)||0;var greyLevel=parseInt(params.options.greyLevel)||0;contrast=-contrast;if(Pixastic.Client.hasCanvasImageData()){var data=Pixastic.prepareData(params);var dataCopy=Pixastic.prepareData(params,true)
var kernel=[[-1,-1,-1],[-1,8,-1],[-1,-1,-1]];var weight=1/8;var rect=params.options.rect;var w=rect.width;var h=rect.height;var w4=w*4;var y=h;do{var offsetY=(y-1)*w4;var nextY=(y==h)?y-1:y;var prevY=(y==1)?0:y-2;var offsetYPrev=prevY*w*4;var offsetYNext=nextY*w*4;var x=w;do{var offset=offsetY+(x*4-4);var offsetPrev=offsetYPrev+((x==1)?0:x-2)*4;var offsetNext=offsetYNext+((x==w)?x-1:x)*4;var r=((-dataCopy[offsetPrev-4]
-dataCopy[offsetPrev]
-dataCopy[offsetPrev+4]
-dataCopy[offset-4]
-dataCopy[offset+4]
-dataCopy[offsetNext-4]
-dataCopy[offsetNext]
-dataCopy[offsetNext+4])
+dataCopy[offset]*8)*weight;var g=((-dataCopy[offsetPrev-3]
-dataCopy[offsetPrev+1]
-dataCopy[offsetPrev+5]
-dataCopy[offset-3]
-dataCopy[offset+5]
-dataCopy[offsetNext-3]
-dataCopy[offsetNext+1]
-dataCopy[offsetNext+5])
+dataCopy[offset+1]*8)*weight;var b=((-dataCopy[offsetPrev-2]
-dataCopy[offsetPrev+2]
-dataCopy[offsetPrev+6]
-dataCopy[offset-2]
-dataCopy[offset+6]
-dataCopy[offsetNext-2]
-dataCopy[offsetNext+2]
-dataCopy[offsetNext+6])
+dataCopy[offset+2]*8)*weight;var brightness=((r+g+b)/3)+greyLevel;if(contrast!=0){if(brightness>127){brightness+=((brightness+1)-128)*contrast;}else if(brightness<127){brightness-=(brightness+1)*contrast;}}
if(invert){brightness=255-brightness;}
if(brightness<0)brightness=0;if(brightness>255)brightness=255;data[offset]=data[offset+1]=data[offset+2]=brightness;}while(--x);}while(--y);return true;}},checkSupport:function(){return Pixastic.Client.hasCanvasImageData();}}
Pixastic.Actions.removenoise={process:function(params){if(Pixastic.Client.hasCanvasImageData()){var data=Pixastic.prepareData(params);var rect=params.options.rect;var w=rect.width;var h=rect.height;var w4=w*4;var y=h;do{var offsetY=(y-1)*w4;var nextY=(y==h)?y-1:y;var prevY=(y==1)?0:y-2;var offsetYPrev=prevY*w*4;var offsetYNext=nextY*w*4;var x=w;do{var offset=offsetY+(x*4-4);var offsetPrev=offsetYPrev+((x==1)?0:x-2)*4;var offsetNext=offsetYNext+((x==w)?x-1:x)*4;var minR,maxR,minG,maxG,minB,maxB;minR=maxR=data[offsetPrev];var r1=data[offset-4],r2=data[offset+4],r3=data[offsetNext];if(r1<minR)minR=r1;if(r2<minR)minR=r2;if(r3<minR)minR=r3;if(r1>maxR)maxR=r1;if(r2>maxR)maxR=r2;if(r3>maxR)maxR=r3;minG=maxG=data[offsetPrev+1];var g1=data[offset-3],g2=data[offset+5],g3=data[offsetNext+1];if(g1<minG)minG=g1;if(g2<minG)minG=g2;if(g3<minG)minG=g3;if(g1>maxG)maxG=g1;if(g2>maxG)maxG=g2;if(g3>maxG)maxG=g3;minB=maxB=data[offsetPrev+2];var b1=data[offset-2],b2=data[offset+6],b3=data[offsetNext+2];if(b1<minB)minB=b1;if(b2<minB)minB=b2;if(b3<minB)minB=b3;if(b1>maxB)maxB=b1;if(b2>maxB)maxB=b2;if(b3>maxB)maxB=b3;if(data[offset]>maxR){data[offset]=maxR;}else if(data[offset]<minR){data[offset]=minR;}
if(data[offset+1]>maxG){data[offset+1]=maxG;}else if(data[offset+1]<minG){data[offset+1]=minG;}
if(data[offset+2]>maxB){data[offset+2]=maxB;}else if(data[offset+2]<minB){data[offset+2]=minB;}}while(--x);}while(--y);return true;}},checkSupport:function(){return Pixastic.Client.hasCanvasImageData();}}
Pixastic.Actions.unsharpmask={process:function(params){var amount=(parseFloat(params.options.amount)||0);var blurAmount=parseFloat(params.options.radius)||0;var threshold=parseFloat(params.options.threshold)||0;amount=Math.min(500,Math.max(0,amount))/2;blurAmount=Math.min(5,Math.max(0,blurAmount))/10;threshold=Math.min(255,Math.max(0,threshold));threshold--;var thresholdNeg=-threshold;amount*=0.016;amount++;if(Pixastic.Client.hasCanvasImageData()){var rect=params.options.rect;var blurCanvas=document.createElement("canvas");blurCanvas.width=params.width;blurCanvas.height=params.height;var blurCtx=blurCanvas.getContext("2d");blurCtx.drawImage(params.canvas,0,0);var scale=2;var smallWidth=Math.round(params.width/scale);var smallHeight=Math.round(params.height/scale);var copy=document.createElement("canvas");copy.width=smallWidth;copy.height=smallHeight;var steps=Math.round(blurAmount*20);var copyCtx=copy.getContext("2d");for(var i=0;i<steps;i++){var scaledWidth=Math.max(1,Math.round(smallWidth-i));var scaledHeight=Math.max(1,Math.round(smallHeight-i));copyCtx.clearRect(0,0,smallWidth,smallHeight);copyCtx.drawImage(blurCanvas,0,0,params.width,params.height,0,0,scaledWidth,scaledHeight);blurCtx.clearRect(0,0,params.width,params.height);blurCtx.drawImage(copy,0,0,scaledWidth,scaledHeight,0,0,params.width,params.height);}
var data=Pixastic.prepareData(params);var blurData=Pixastic.prepareData({canvas:blurCanvas,options:params.options});var w=rect.width;var h=rect.height;var w4=w*4;var y=h;do{var offsetY=(y-1)*w4;var x=w;do{var offset=offsetY+(x*4-4);var difR=data[offset]-blurData[offset];if(difR>threshold||difR<thresholdNeg){var blurR=blurData[offset];blurR=amount*difR+blurR;data[offset]=blurR>255?255:(blurR<0?0:blurR);}
var difG=data[offset+1]-blurData[offset+1];if(difG>threshold||difG<thresholdNeg){var blurG=blurData[offset+1];blurG=amount*difG+blurG;data[offset+1]=blurG>255?255:(blurG<0?0:blurG);}
var difB=data[offset+2]-blurData[offset+2];if(difB>threshold||difB<thresholdNeg){var blurB=blurData[offset+2];blurB=amount*difB+blurB;data[offset+2]=blurB>255?255:(blurB<0?0:blurB);}}while(--x);}while(--y);return true;}},checkSupport:function(){return Pixastic.Client.hasCanvasImageData();}}