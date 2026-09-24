import { useEffect, useRef, useState } from 'react';
import { assetUrl } from './lib/assets';

export default function HeroPortrait(){
 const canvas=useRef<HTMLCanvasElement>(null);const [ready,setReady]=useState(false);
 useEffect(()=>{const node=canvas.current;if(!node)return;const ctx=node.getContext('2d',{alpha:false});if(!ctx)return;
 let cancelled=false;let cleanup=()=>{};
 async function init(){try{const res=await fetch(assetUrl('portrait/manifest.json'));if(!res.ok)return;const manifest=await res.json() as {frames:string[],width:number,height:number};if(!manifest.frames?.length)return;
 const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;const images:Array<HTMLImageElement|undefined>=new Array(manifest.frames.length);let target=0;let last=-1;
 node!.width=manifest.width;node!.height=manifest.height;
 function draw(index:number){target=index;if(cancelled)return;let img=images[index];if(!img){for(let d=1;d<images.length;d++){img=images[index-d]??images[index+d];if(img)break;}}if(!img||last===index)return;ctx!.drawImage(img,0,0,node!.width,node!.height);last=index;node!.dataset.frame=String(index);}
 const load=(index:number)=>new Promise<void>(resolve=>{const img=new Image();img.decoding='async';img.onload=()=>{if(!cancelled){images[index]=img;last=-1;if(index===0||index===target)draw(target);if(index===0)setReady(true);}resolve();};img.onerror=()=>resolve();img.src=assetUrl(manifest.frames[index]);});
 await load(0);if(cancelled||reduce)return;
 const [g,s]=await Promise.all([import('gsap'),import('gsap/ScrollTrigger')]);if(cancelled)return;g.gsap.registerPlugin(s.ScrollTrigger);
 document.querySelector('.hero-track')?.classList.add('has-sequence');
 const trigger=s.ScrollTrigger.create({trigger:'.hero-track',start:'top top',end:'bottom bottom',onUpdate:self=>{draw(Math.round(self.progress*(manifest.frames.length-1)));const hint=document.querySelector<HTMLElement>('.scroll-hint');if(hint)hint.style.opacity=String(Math.max(0,1-self.progress*8));}});
 cleanup=()=>trigger.kill();s.ScrollTrigger.refresh();
 // A small concurrent queue keeps first paint light while preparing the turntable.
 let next=1;await Promise.all(Array.from({length:5},async()=>{while(next<manifest.frames.length&&!cancelled){await load(next++);}}));draw(target);
 }catch{/* The studio portrait remains available if the sequence cannot load. */}}
 init();return()=>{cancelled=true;cleanup();document.querySelector('.hero-track')?.classList.remove('has-sequence');};},[]);
 return <div className="portrait-stage"><img className={'portrait-fallback '+(ready?'is-hidden':'')} src={assetUrl('images/portrait.webp')} alt="Retrato de Maurício Taguchi" width={1086} height={1448} fetchPriority="high"/><canvas ref={canvas} className={ready?'portrait-canvas is-ready':'portrait-canvas'} role="img" aria-hidden={!ready} aria-label="Retrato de Maurício Taguchi que gira conforme a rolagem"/></div>;
}
