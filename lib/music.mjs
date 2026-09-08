// Original, locally synthesized score. No downloads or copyrighted recordings.
export const MUSIC_THEMES=[
 {id:'desert',title:'尘暴追猎',bpm:126,root:38,scale:[0,1,3,5,7,8,10],bass:[0,0,3,1],lead:[0,4,1,5,2,4,1,6],wave:'sawtooth'},
 {id:'city',title:'钢铁封锁',bpm:140,root:33,scale:[0,2,3,5,6,8,10],bass:[0,0,4,1],lead:[0,3,4,1,0,6,4,2],wave:'square'},
 {id:'mud',title:'边境暗涌',bpm:112,root:36,scale:[0,2,3,5,7,8,10],bass:[0,2,5,3],lead:[0,2,4,6,5,4,2,1],wave:'triangle'},
 {id:'snow',title:'白色警戒',bpm:118,root:42,scale:[0,2,3,5,7,9,10],bass:[0,3,5,2],lead:[6,4,2,0,3,5,4,1],wave:'sine'}
];
export class BattleMusic{
 constructor(context){this.ctx=context;this.nodes=new Set();this.master=context.createGain();this.master.gain.value=.30;this.master.connect(context.destination);this.mix=context.createGain();this.mix.gain.value=0;this.compressor=context.createDynamicsCompressor();this.mix.connect(this.compressor);this.compressor.connect(this.master);this.noise=context.createBuffer(1,context.sampleRate,context.sampleRate);let data=this.noise.getChannelData(0),seed=914;for(let i=0;i<data.length;i++){seed=(seed*1664525+1013904223)>>>0;data[i]=seed/2147483648-1;}this.timer=setInterval(()=>this.schedule(),35);this.intensity=.5;}
 track(node){this.nodes.add(node);node.onended=()=>{node.disconnect();this.nodes.delete(node)};return node;}
 tone(midi,start,duration,volume,wave='triangle',cutoff=1400,bus=this.mix){const a=this.ctx,osc=this.track(a.createOscillator()),gain=a.createGain(),filter=a.createBiquadFilter();osc.isStinger=bus===this.master;osc.type=wave;osc.frequency.value=440*Math.pow(2,(midi-69)/12);filter.type='lowpass';filter.frequency.value=cutoff;gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(volume,start+.016);gain.gain.exponentialRampToValueAtTime(.0001,start+duration);osc.connect(filter);filter.connect(gain);gain.connect(bus);osc.start(start);osc.stop(start+duration+.03);osc.addEventListener('ended',()=>{gain.disconnect();filter.disconnect()});}
 drum(time,type){const a=this.ctx,g=a.createGain();g.connect(this.mix);if(type==='kick'){const o=this.track(a.createOscillator());o.frequency.setValueAtTime(130,time);o.frequency.exponentialRampToValueAtTime(38,time+.19);g.gain.setValueAtTime(.34,time);g.gain.exponentialRampToValueAtTime(.001,time+.23);o.connect(g);o.start(time);o.stop(time+.25);o.addEventListener('ended',()=>g.disconnect());}else{const n=this.track(a.createBufferSource()),f=a.createBiquadFilter();n.buffer=this.noise;f.type='highpass';f.frequency.value=type==='hat'?6500:1700;n.connect(f);f.connect(g);const duration=type==='hat'?.045:.16;g.gain.setValueAtTime(type==='hat'?.045:.12,time);g.gain.exponentialRampToValueAtTime(.0001,time+duration);n.start(time);n.stop(time+duration+.01);n.addEventListener('ended',()=>{f.disconnect();g.disconnect()});}}
 setMuted(muted){this.master.gain.setTargetAtTime(muted?0:.30,this.ctx.currentTime,.06);}
 play(map){if(this.map!==map){this.stop();this.map=map;this.step=0;}this.theme=MUSIC_THEMES[map];this.active=true;this.next=this.ctx.currentTime+.06;this.mix.gain.setTargetAtTime(1,this.ctx.currentTime,.4);this.schedule();}
 setPaused(paused){if(paused){if(this.active)this.stop(false);}else if(this.theme&&!this.active)this.play(this.map);}
 stop(reset=true,all=false){this.active=false;this.mix.gain.setTargetAtTime(0,this.ctx.currentTime,.04);for(const n of this.nodes){if(!all&&n.isStinger)continue;try{n.stop(this.ctx.currentTime+.15)}catch{}}if(reset)this.step=0;}
 schedule(){if(!this.active||this.ctx.state!=='running')return;if(this.next<this.ctx.currentTime)this.next=this.ctx.currentTime+.03;const t=this.theme,interval=60/t.bpm/4;while(this.next<this.ctx.currentTime+.15){const step=this.step%64,bar=Math.floor(step/16),beat=step%16,root=t.root+t.scale[t.bass[bar]];
 if(beat%4===0||t.id==='city'&&beat===14)this.drum(this.next,'kick');if(beat===4||beat===12)this.drum(this.next,'snare');if(beat%2===0||this.intensity>.7)this.drum(this.next,'hat');
 if(beat%2===0)this.tone(root+(beat===14?12:0),this.next,interval*1.65,.16,t.wave,t.id==='city'?600:850);
 if(beat===0){for(const offset of [0,7,12])this.tone(root+12+offset,this.next,interval*15,.038,'sawtooth',t.id==='snow'?650:950);}
 if(beat%2===0){const note=t.root+24+t.scale[t.lead[(step/2)%8]];this.tone(note,this.next,interval*(t.id==='snow'?3:1.3),.05+this.intensity*.025,t.id==='snow'?'sine':'triangle',2100);if(t.id==='snow')this.tone(note+12,this.next+interval*.75,interval*2,.025,'sine',3500);}
 this.next+=interval;this.step++;}}
 celebrate(count){const now=this.ctx.currentTime;for(let i=0;i<count+2;i++)this.tone(60+[0,7,12,15,19,24,27][i],now+i*.075,.6,.14,'triangle',3200,this.master);}
 dispose(){clearInterval(this.timer);this.stop(true,true);this.master.disconnect();this.mix.disconnect();this.compressor.disconnect();}
}
