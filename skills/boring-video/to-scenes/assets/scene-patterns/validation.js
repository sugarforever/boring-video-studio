/* Preflight returns proposals; it never changes input or renders a scene. */
(function(){
  const segmenter=new Intl.Segmenter('en',{granularity:'grapheme'});
  function columns(text){
    let width=0;
    for(const {segment}of segmenter.segment(String(text))){
      if(segment==='\t'){width+=8-width%8;continue;}
      if(/^\p{Mark}+$/u.test(segment))continue;
      width+=/[\u1100-\u115f\u2e80-\ua4cf\uac00-\ud7a3\uf900-\ufaff\ufe10-\ufe6f\uff01-\uff60\uffe0-\uffe6]|\p{Extended_Pictographic}|\p{Regional_Indicator}|\u20e3/u.test(segment)?2:1;
    }return width;
  }
  const proposal=(action,label,changes)=>({action,label,requiresConfirmation:true,...(changes?{changes}:{})});
  const textSuggestions=()=>[proposal('shorten','精简文案并保留含义'),proposal('paginate','拆成多个场景'),proposal('redesign','调整项目模板布局和预算后重新校验')];
  function excerpt(text,max){let out='';for(const {segment}of segmenter.segment(String(text))){if(columns(out+segment)>max-1)break;out+=segment;}return out+'…';}
  function validate(id,props,options,derive){
    const issues=[],record=window.SCENE_CATALOG.find(v=>v.id===id);
    const add=(path,rule,actual,limit,message,suggestions=textSuggestions())=>issues.push({path,rule,actual,limit,message,suggestions});
    const result=()=>({ok:!issues.length,id,revision:record?.revision,theme:options.theme||'blockframe',mode:options.mode||'light',requiresConfirmation:!!issues.length,issues});
    if(!record){add('id','known-pattern',id,null,'选择目录中存在的模板');return result();}
    if(options.revision!==undefined&&String(options.revision)!==record.revision){add('revision','matching-revision',options.revision,record.revision,'使用该选择所固定的原始实现，或确认迁移配置');return result();}
    if(options.time!==undefined&&(typeof options.time!=='number'||!Number.isFinite(options.time)))add('options.time','finite-number',String(options.time),null,'时间必须是有限数值');
    if(!SceneThemes.keys[options.theme||'blockframe']||!['light','dark'].includes(options.mode||'light')){add('options','known-appearance',options,null,'选择已支持的风格与模式');return result();}
    if(!props||typeof props!=='object'||Array.isArray(props)){add('props','object',typeof props,null,'配置必须是对象');return result();}
    for(const key of Object.keys(props))if(!['title','copy','data','source','media'].includes(key))add(key,'known-field',key,null,'使用 revision 3 的配置字段');
    if(props.data!==undefined&&(!props.data||typeof props.data!=='object'||Array.isArray(props.data)))add('data','object',typeof props.data,null,'data 必须是对象');
    if(props.copy!==undefined&&(!props.copy||typeof props.copy!=='object'||Array.isArray(props.copy)))add('copy','object',typeof props.copy,null,'copy 必须是原文与替换文的映射');
    if(issues.length)return result();
    const p={...record.example,...props,data:{...record.example.data,...props.data}},rules=record.validation,defaults=SCENE_LIBRARY.validationDefaults;
    const text=(path,value,max)=>{
      if(typeof value!=='string'&&typeof value!=='number'){add(path,'text-or-number',typeof value,null,'该展示字段需要文字或数值');return;}
      const width=columns(value);if(width>max)add(path,'max-columns',width,max,'显示宽度超过该字段预算');
    };
    if(props.title!==undefined){if(typeof props.title!=='string'||!props.title.trim())add('title','nonempty-text',props.title,null,'填写标题，或移除 title 沿用案例标题');else text('title',props.title,rules.titleColumns);}
    for(const [key,replacement]of Object.entries(p.copy||{})){
      if(typeof replacement!=='string'){add('copy.'+key,'text',typeof replacement,null,'替换文必须是字符串');continue;}
      text('copy.'+key,replacement,Math.min(defaults.copyMaxColumns,Math.max(defaults.copyMinColumns,Math.ceil(columns(key)*defaults.copyExpansion))));
    }
    const optional=rules.source?.focusValueColumns?['focusPreview']:[];
    for(const key of Object.keys(p.data))if(!Object.hasOwn(record.example.data,key)&&!optional.includes(key))add('data.'+key,'known-field',key,null,'该模板不支持此数据字段');
    const targets=(path)=>{
      let found=[{path:'',value:p}];
      for(const key of path.split('.'))found=found.flatMap(item=>key==='*'?(Array.isArray(item.value)?item.value.map((value,k)=>({path:item.path+'.'+k,value})):[]):[{path:item.path?item.path+'.'+key:key,value:item.value?.[key]}]);
      return found;
    };
    for(const rule of rules.fields){
      for(const item of targets(rule.path)){
        if(rule.maxColumns!==undefined)text(item.path,item.value,rule.maxColumns);
        if(rule.maxItems!==undefined){
          if(!Array.isArray(item.value)){add(item.path,'array',typeof item.value,null,'该字段需要数组');continue;}
          if(item.value.length<rule.minItems||item.value.length>rule.maxItems)add(item.path,'item-count',item.value.length,{min:rule.minItems,max:rule.maxItems},'项目数量超出该模板范围',[proposal('select','选择本场景需要的项目，保留其余原始数据'),proposal('paginate','按项目拆成多个场景'),proposal('redesign','调整项目模板布局和预算后重新校验')]);
        }
      }
    }
    if(rules.source){
      const n=p.data,b=rules.source;
      if(typeof n.source!=='string')add('data.source','text',typeof n.source,null,'源码必须是字符串');
      else{
        const lines=n.source.replace(/\r\n?/g,'\n').split('\n');
        if(/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]/.test(n.source))add('data.source','displayable-text',null,null,'源码含不可直接展示的控制字符',[proposal('clean-format','确认清理样式控制码，保留正文和顺序'),proposal('replay','终端控制序列改用 record-terminal 回放')]);
        if(lines.length>b.maxLines)add('data.source','max-lines',lines.length,b.maxLines,'源码行数超过页面预算',[proposal('paginate','按逻辑拆页；JSON/XML 每页保持可解析'),proposal('excerpt','确认标注节选后，选取完整的相关片段')]);
        lines.forEach((line,k)=>text('data.source.line['+(k+1)+']',line,b.maxLineColumns));
      }
      text('data.fileName',n.fileName,b.fileNameColumns);
    }
    if(issues.length)return result();
    if(rules.minSegmentShare){
      const total=p.data.segments.reduce((sum,row)=>sum+row[1],0);
      p.data.segments.forEach((row,k)=>{const share=row[1]/total;if(share<rules.minSegmentShare)add('data.segments.'+k,'min-display-share',share,rules.minSegmentShare,'该分段太窄，标签可能重叠',[proposal('callout','改用独立标注或单独场景'),proposal('group','确认可合并的小项，并标明合并口径'),proposal('change-pattern','改用等宽表格，保留原始时长')]);});
    }
    if(rules.pointSeparation){
      const n=p.data,minimum=rules.pointSeparation;
      n.points.forEach((row,k)=>n.points.slice(k+1).forEach((other,j)=>{if(Math.abs(row[1]-other[1])/n.xMax<minimum.x&&Math.abs(row[2]-other[2])/n.yMax<minimum.y)add('data.points.'+(k+j+1),'point-separation',{near:k},minimum,'点位与标签过密',[proposal('callout','保留坐标，用引线分离标签'),proposal('paginate','分镜比较这些点位'),proposal('change-pattern','改用表格；保持原始数值')]);}));
    }
    if(issues.length)return result();
    let d;
    try{d=derive(id,p,SceneThemes.resolve(SceneThemes.keys[options.theme||'blockframe'],options.mode||'light'),false);}
    catch(error){
      const field=['focusPreview','focusPath','focusTag','highlightLine','language','files'].find(key=>error.message.includes(key));
      add(field?'data.'+field:rules.source?'data.source':'data','valid-content',field?p.data[field]:null,null,error.message,[proposal('repair','核对格式、路径、索引、单位和取值范围后确认修订'),proposal('change-pattern','改用适合片段或长内容的模板')]);return result();
    }
    if(rules.source&&d.code){
      const b=rules.source;
      for(const key of ['focusLabel','focusValue']){
        const max=b[key+'Columns'];if(max===undefined)continue;
        const value=d.code[key].replace(/\s+/g,' ').trim(),width=columns(value);
        if(width>max){
          const suggestions=key==='focusValue'?[proposal('excerpt','仅节选侧栏值，保留完整源码',[{path:'data.focusPreview',value:excerpt(value,max)}]),proposal('refocus','改为聚焦较短的叶节点'),proposal('redesign','扩大项目模板的侧栏并重新校验')]:[proposal('refocus','选择较短且无歧义的字段路径'),proposal('redesign','调整侧栏路径布局并重新校验')];
          add('data.'+key,'max-columns',width,max,'解析后的聚焦内容超过侧栏预算',suggestions);
        }
      }
    }
    return result();
  }
  window.SceneValidation={validate,columns};
})();
