<script setup lang="ts">
import { computed, useId } from 'vue'
import type { Binding, Cell, Metric, MetricResult } from '../contracts/types'
import { areaNames } from '../data/fixtures.mjs'
const props=defineProps<{kind:'hologram'|'astral';binding:Binding;metric:Metric;result:MetricResult}>()
const emit=defineEmits<{select:[filter:string,value:Cell]}>()
const uid=`spectral-${useId().replace(/[^a-zA-Z0-9_-]/g,'')}`
// Concept positions and crystal dimensions are decorative, never geographic or data encodings.
const anchors:Record<string,number[]>={north:[190,125],east:[710,170],south:[180,338],west:[720,370]}
const zones=computed(()=>props.result.rows.flatMap(row=>{
 const id=String(row[props.binding.fields.label!]),p=anchors[id]
 return p?[{id,x:p[0],y:p[1],value:row[props.binding.fields.value!]}]:[]
}))
const stars=Array.from({length:96},(_,i)=>({x:40+(i*137.51)%820,y:28+(i*71.39)%445,r:i%13===0?1.8:.5+(i%3)*.3}))
function select(id:string):void{if(props.binding.interaction)emit('select',props.binding.interaction.filter,id)}
</script>
<template>
 <div class="spectral-scene" :data-concept="kind">
  <svg viewBox="60 48 780 430" role="img" :aria-label="kind==='hologram'?'晶体反应场概念示意，形状与光柱不代表业务数值':'星图展陈概念示意，轨道不代表地理与业务连线'">
   <defs>
    <radialGradient :id="`${uid}-aura`"><stop stop-color="var(--accent)" stop-opacity=".4"/><stop offset=".5" stop-color="var(--accent)" stop-opacity=".12"/><stop offset="1" stop-color="var(--accent)" stop-opacity="0"/></radialGradient>
    <radialGradient :id="`${uid}-sphere`" cx="30%" cy="25%"><stop stop-color="var(--accent)" stop-opacity=".42"/><stop offset=".55" stop-color="var(--surface)" stop-opacity=".6"/><stop offset="1" stop-color="var(--background)" stop-opacity=".9"/></radialGradient>
    <linearGradient :id="`${uid}-crystal`" x1="0" y1="0" x2="1" y2="1"><stop stop-color="var(--text)" stop-opacity=".65"/><stop offset=".27" stop-color="var(--accent)" stop-opacity=".13"/><stop offset=".74" stop-color="var(--accent)" stop-opacity=".38"/><stop offset="1" stop-color="var(--surface)" stop-opacity=".6"/></linearGradient>
    <linearGradient :id="`${uid}-beam`" x1="0" y1="1" x2="0" y2="0"><stop stop-color="var(--accent)" stop-opacity=".27"/><stop offset="1" stop-color="var(--accent)" stop-opacity="0"/></linearGradient>
   </defs>
   <template v-if="kind==='hologram'">
    <ellipse cx="450" cy="320" rx="310" ry="180" :fill="`url(#${uid}-aura)`"/>
    <g class="reactor-columns fx"><path d="M265 399L285 70H320L340 399Z M565 399L582 70H617L637 399Z" :fill="`url(#${uid}-beam)`"/><path d="M410 390L423 15H477L490 390Z" :fill="`url(#${uid}-beam)`"/></g>
    <g v-for="(y,i) in [325,364,404]" :key="y" :transform="`translate(450,${y})`" class="reactor-ring"><ellipse :rx="234-i*18" :ry="63-i*4" :fill="i===2?'var(--surface)':'none'" fill-opacity=".45"/><ellipse :rx="220-i*18" :ry="55-i*4"/><ellipse :rx="244-i*18" :ry="65-i*4" class="reactor-ticks fx"/><path d="M-215 0H-160 M160 0H215 M0 -56V-42 M0 42V56"/></g>
    <g class="reactor-supports"><path d="M265 333V410 M635 333V410 M450 387V467"/><path d="M292 367V418 M608 367V418"/></g>
    <g class="reactor-crystal">
     <path d="M450 74L547 143L532 277L450 334L368 277L353 143Z" :fill="`url(#${uid}-crystal)`"/>
     <path d="M450 74L450 194L353 143 M450 194L547 143 M450 194L450 334 M368 277L450 194L532 277" class="crystal-facets"/>
     <path d="M450 105L515 154L504 260L450 300L396 260L385 154Z" class="crystal-inner"/>
     <path d="M450 105V300 M385 154L450 181L515 154 M396 260L450 225L504 260" class="crystal-inner"/>
     <path d="M353 143L450 74L547 143 M368 277L450 334L532 277" class="crystal-edge optical-glow"/>
     <ellipse cx="450" cy="197" rx="137" ry="28" class="reactor-scan fx"/>
    </g>
    <g class="reactor-satellites"><path v-for="(p,i) in [[299,187],[603,246],[345,330]]" :key="i" :d="`M${p[0]} ${p[1]-18}l13 18l-13 18l-13 -18Z`"/></g>
    <path d="M275 449H370L393 465H507L530 449H625" class="reactor-baseline"/>
   </template>
   <template v-else>
    <ellipse cx="470" cy="240" rx="340" ry="207" :fill="`url(#${uid}-aura)`" transform="rotate(-22 470 240)"/>
    <g class="astral-specks"><circle v-for="(s,i) in stars" :key="i" :cx="s.x" :cy="s.y" :r="s.r" :opacity=".2+(i%5)*.12"/></g>
    <ellipse cx="450" cy="252" rx="300" ry="114" transform="rotate(-23 450 252)" class="celestial-orbit orbit-back"/>
    <circle cx="450" cy="246" r="137" :fill="`url(#${uid}-sphere)`" class="celestial-sphere"/>
    <g class="celestial-graticule"><ellipse cx="450" cy="246" rx="137" ry="39"/><ellipse cx="450" cy="194" rx="125" ry="30"/><ellipse cx="450" cy="298" rx="125" ry="30"/><ellipse cx="450" cy="153" rx="101" ry="19"/><ellipse cx="450" cy="339" rx="101" ry="19"/><ellipse cx="450" cy="246" rx="45" ry="137"/><ellipse cx="450" cy="246" rx="98" ry="137"/><path d="M450 109V383"/></g>
    <path d="M385 155L413 183L467 169L509 211L489 254L527 287 M370 244L403 268L425 319L478 345" class="celestial-constellation"/>
    <g class="celestial-nodes"><circle v-for="(p,i) in [[385,155],[413,183],[467,169],[509,211],[489,254],[527,287],[370,244],[403,268],[425,319],[478,345]]" :key="i" :cx="p[0]" :cy="p[1]" r="2.5"/></g>
    <ellipse cx="450" cy="252" rx="311" ry="120" transform="rotate(-23 450 252)" class="celestial-orbit orbit-dashes fx"/>
    <path d="M164 373C160 410 300 401 448 331S720 175 736 135" class="celestial-orbit orbit-front optical-glow"/>
    <ellipse cx="450" cy="246" rx="170" ry="190" transform="rotate(40 450 246)" class="celestial-orbit orbit-upright"/>
    <g class="orbital-satellites"><circle cx="671" cy="159" r="9"/><circle cx="244" cy="356" r="6"/><circle cx="551" cy="87" r="4"/></g>
    <path d="M125 460H330 M570 460H775" class="celestial-baseline"/><path d="M450 432l7 12l-7 12l-7 -12Z" class="celestial-jewel"/>
   </template>
   <g v-for="zone in zones" :key="zone.id" :transform="`translate(${zone.x},${zone.y})`" class="spectral-zone" role="button" tabindex="0" :aria-label="`选择${areaNames[zone.id as keyof typeof areaNames]}`" @click="select(zone.id)" @keydown.enter="select(zone.id)" @keydown.space.prevent="select(zone.id)">
    <path :d="zone.x<450?'M65 12H97L117 32':'M-65 12H-97L-117 32'" class="spectral-leader"/>
    <path v-if="kind==='hologram'" d="M-67 -12H56L68 0V43H-56L-68 31Z" class="spectral-tag"/>
    <rect v-else x="-70" y="-12" width="140" height="55" rx="14" class="spectral-tag"/>
    <text x="-52" y="6" class="campus-zone-name">{{ areaNames[zone.id as keyof typeof areaNames] }}</text>
    <text x="-52" y="28" class="campus-zone-value">{{ typeof zone.value==='number' ? zone.value.toLocaleString('zh-CN') : '—' }} <tspan class="campus-zone-unit">{{ metric.unit }}</tspan></text>
   </g>
  </svg>
  <p class="campus-note">{{ kind==='hologram'?'晶体反应场':'星图展陈' }}概念示意 · 非地理模型 <span>选择区域联动数据</span></p>
  <div class="campus-scope"><span>当前数据覆盖</span><strong>{{ zones.length }} 个区域</strong></div>
 </div>
</template>
