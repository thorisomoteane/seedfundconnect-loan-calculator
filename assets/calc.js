/* ============================================================
   SeedFund Connect — ECD Loan Calculator
   Shared math, formatting, and storage. Ports
   ecd_loan_calculator (1).py exactly, so every figure the site
   shows matches what the CLI script would print. Loaded by
   index.html, applications.html and print.html.
   ============================================================ */
window.ECD = (function(){
  "use strict";

  // ---------------- core math ----------------
  function pmt(principal, i, n){
    if(n<=0) return 0;
    if(i===0) return principal/n;
    return principal*i/(1-Math.pow(1+i,-n));
  }
  function maxLoan(payment, i, n){
    if(n<=0 || payment<=0) return 0;
    if(i===0) return payment*n;
    return payment*(1-Math.pow(1+i,-n))/i;
  }

  function repaymentReport(amount, annualRate, term, grace, initFee, initFinanced, serviceFee){
    var i = annualRate/100/12;
    var financed = amount + (initFinanced ? initFee : 0);
    var start = financed;
    for(var g=0; g<grace; g++){ start += start*i; }
    var payN = Math.max(1, term-grace);
    var instalment = pmt(start, i, payN);
    var allIn = instalment + serviceFee;

    var balance = financed, totalInterest = 0;
    var schedule = [{m:0, opening:financed, instal:null, interest:null, principal:null, serviceFee:null, total:null, balance:financed, isGrace:false}];
    for(var m=1; m<=term; m++){
      var opening = balance, interest = balance*i, instal, principal;
      var isGrace = m<=grace;
      if(isGrace){ instal = 0; principal = -interest; balance += interest; }
      else { instal = instalment; principal = instal-interest; balance -= principal; if(balance<0.5) balance = 0; }
      totalInterest += Math.max(interest,0);
      schedule.push({m:m, opening:opening, instal:instal, interest:interest, principal:principal,
                      serviceFee:serviceFee, total:instal+serviceFee, balance:balance, isGrace:isGrace});
    }
    var totalService = serviceFee*term;
    var totalFees = initFee + totalService;
    var totalRepayable = instalment*payN + totalService + (initFinanced ? 0 : initFee);
    var costPct = amount>0 ? (totalRepayable-amount)/amount*100 : 0;

    return {instalment:instalment, allIn:allIn, totalInterest:totalInterest, totalService:totalService,
            totalFees:totalFees, totalRepayable:totalRepayable, costPct:costPct, schedule:schedule, financed:financed};
  }

  function affordabilityReport(capacity, annualRate, term, target, initFee, initFinanced, serviceFee){
    var i = annualRate/100/12;
    var avail = capacity - serviceFee;
    if(avail<=0){ return {avail:avail, insufficient:true}; }

    var maxFin = maxLoan(avail, i, term);
    var maxToApplicant = Math.max(0, maxFin - (initFinanced ? initFee : 0));
    var byTerm = [12,24,36,48,60].map(function(t){
      var mf = maxLoan(avail, i, t);
      return {t:t, amount: Math.max(0, mf - (initFinanced ? initFee : 0))};
    });

    var out = {avail:avail, insufficient:false, maxToApplicant:maxToApplicant, byTerm:byTerm, hasTarget:target>0};
    if(target>0){
      var targetFin = target + (initFinanced ? initFee : 0);
      var months;
      if(i===0){ months = targetFin/avail; }
      else if(avail <= targetFin*i){ months = Infinity; }
      else { months = -Math.log(1 - targetFin*i/avail) / Math.log(1+i); }
      out.months = months;
      if(maxToApplicant >= target) out.verdict = "OK";
      else if(months !== Infinity && months<=60) out.verdict = "RIGHT-SIZE";
      else out.verdict = "DECLINE";
    }
    return out;
  }

  // ---------------- formatting ----------------
  function rand(x){ return (x<0?"-R":"R") + Math.abs(Math.round(x)).toLocaleString("en-US"); }
  function rand2(x){ return (x<0?"-R":"R") + Math.abs(x).toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2}); }
  function esc(s){ var d=document.createElement("div"); d.textContent=s; return d.innerHTML; }
  function fmtDate(iso){
    try{
      return new Date(iso).toLocaleDateString("en-ZA", {year:"numeric", month:"short", day:"numeric"});
    }catch(e){ return iso; }
  }

  // ---------------- application storage (localStorage — browser-local demo store) ----------------
  var STORAGE_KEY = "sfc_ecd_applications_v1";

  function loadApplications(){
    try{
      var raw = localStorage.getItem(STORAGE_KEY);
      var arr = raw ? JSON.parse(raw) : [];
      return Array.isArray(arr) ? arr : [];
    }catch(e){ return []; }
  }
  function saveApplications(arr){
    try{ localStorage.setItem(STORAGE_KEY, JSON.stringify(arr)); return true; }
    catch(e){ return false; }
  }
  function newId(){
    if(window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return "app_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2,8);
  }
  function addApplication(data){
    var arr = loadApplications();
    var rec = Object.assign({}, data, { id:newId(), savedAt:new Date().toISOString() });
    arr.unshift(rec);
    saveApplications(arr);
    return rec;
  }
  function updateApplication(id, data){
    var arr = loadApplications();
    var idx = arr.findIndex(function(a){ return a.id===id; });
    if(idx===-1) return addApplication(data);
    arr[idx] = Object.assign({}, arr[idx], data, { id:id, savedAt:new Date().toISOString() });
    saveApplications(arr);
    return arr[idx];
  }
  function deleteApplication(id){
    var arr = loadApplications().filter(function(a){ return a.id!==id; });
    saveApplications(arr);
  }
  function getApplication(id){
    return loadApplications().find(function(a){ return a.id===id; }) || null;
  }

  // draft handoff for "print without saving" from the calculator
  var DRAFT_KEY = "sfc_ecd_print_draft";
  function setPrintDraft(data){ try{ sessionStorage.setItem(DRAFT_KEY, JSON.stringify(data)); }catch(e){} }
  function getPrintDraft(){ try{ var raw=sessionStorage.getItem(DRAFT_KEY); return raw?JSON.parse(raw):null; }catch(e){ return null; } }

  return {
    pmt:pmt, maxLoan:maxLoan, repaymentReport:repaymentReport, affordabilityReport:affordabilityReport,
    rand:rand, rand2:rand2, esc:esc, fmtDate:fmtDate,
    loadApplications:loadApplications, saveApplications:saveApplications,
    addApplication:addApplication, updateApplication:updateApplication,
    deleteApplication:deleteApplication, getApplication:getApplication,
    setPrintDraft:setPrintDraft, getPrintDraft:getPrintDraft
  };
})();
