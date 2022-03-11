(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([[0],{110:function(e,t,n){"use strict";n.r(t);var i=n(111);var o=n.n(i);for(var s in i)if(s!=="default")(function(e){n.d(t,e,function(){return i[e]})})(s);t["default"]=o.a},111:function(e,t,n){"use strict";var i=n(0);Object.defineProperty(t,"__esModule",{value:true});t.default=void 0;var o=i(n(81));var s={name:"QuestionRadio",mixins:[o.default],props:{info:{type:Object,default:{question:null,option_A:null,option_B:null,option_C:null,option_D:null,explain:null,answer:null,types:"单选题"}}},data:function e(){return{}},computed:{optionStyle:function e(){var t=this;return function(e){if(e==="A"||e==="C"){if(t.Question.answer===e){return"optionAC choosed-style"}else if(t.mouseOver===e){return"optionAC mouseOver-style"}else{return"optionAC"}}else{if(t.Question.answer===e){return"optionBD choosed-style"}else if(t.mouseOver===e){return"optionBD mouseOver-style"}else{return"optionBD"}}}}},created:function e(){},methods:{choose:function e(t){if(!this.readonly){this.Question.answer=t}},handleSwitcherChange:function e(t){if(!t&&!this.readonly){this.Question.explain=null}},reset:function e(){this.Question.question=null;this.Question.option_A=null;this.Question.option_B=null;this.Question.option_C=null;this.Question.option_D=null;this.Question.answer=null;this.Question.explain=null;this.explainOpen=false;this.$refs.Question.clearError()},nextOption:function e(t){if(t==="A"){this.$refs.optionA.focus()}else if(t==="B"){this.$refs.optionB.focus()}else if(t==="C"){this.$refs.optionC.focus()}else{this.$refs.optionD.focus()}}}};t.default=s},112:function(e,t,n){},113:function(e,t,n){"use strict";n.r(t);var i=n(114);var o=n.n(i);for(var s in i)if(s!=="default")(function(e){n.d(t,e,function(){return i[e]})})(s);t["default"]=o.a},114:function(e,t,n){"use strict";var i=n(0);Object.defineProperty(t,"__esModule",{value:true});t.default=void 0;var o=i(n(81));var s={name:"QuestionRadio",mixins:[o.default],props:{info:{type:Object,default:{question:null,option_A:null,option_B:null,option_C:null,option_D:null,option_E:null,explain:null,answer:[],types:"多选题"}}},data:function e(){return{}},computed:{optionStyle:function e(){var t=this;return function(e){var n=t.Question.answer.indexOf(e);if(e==="A"||e==="C"||e==="E"){if(n>=0){return"optionAC choosed-style"}else if(t.mouseOver===e){return"optionAC mouseOver-style"}else{return"optionAC"}}else{if(n>=0){return"optionBD choosed-style"}else if(t.mouseOver===e){return"optionBD mouseOver-style"}else{return"optionBD"}}}}},created:function e(){if(this.editable){this.Question.answer=this.Question.answer.split("")}},methods:{choose:function e(t){if(this.Question.answer.indexOf(t)<0){this.Question.answer.push(t)}else{this.Question.answer.splice(this.Question.answer.indexOf(t),1)}this.ascending_sort(this.Question.answer)},checkData:function e(){var t=this;this.Question.answer=this.Question.answer.join("");console.log(this.Question.answer);this.$refs.Question.validate().then(function(e){if(t.editable){t.$emit("updateQuestion",t.Question)}else{t.$emit("createQuestion",t.Question)}},function(e){t.config.message=e.content;t.config.theme="error";t.$bkMessage(t.config)});this.Question.answer=this.Question.answer.split("")},ascending_sort:function e(t){return t.sort(function(e,t){var n=e;var i=t;return n<i?-1:n>i?1:0})},reset:function e(){this.Question.question=null;this.Question.option_A=null;this.Question.option_B=null;this.Question.option_C=null;this.Question.option_D=null;this.Question.option_E=null;this.Question.answer=[];this.Question.explain=null;this.explainOpen=false;this.$refs.Question.clearError()},nextOption:function e(t){if(t==="A"){this.$refs.optionA.focus()}else if(t==="B"){this.$refs.optionB.focus()}else if(t==="C"){this.$refs.optionC.focus()}else if(t==="D"){this.$refs.optionD.focus()}else{this.$refs.optionE.focus()}}}};t.default=s},115:function(e,t,n){},116:function(e,t,n){"use strict";n.r(t);var i=n(117);var o=n.n(i);for(var s in i)if(s!=="default")(function(e){n.d(t,e,function(){return i[e]})})(s);t["default"]=o.a},117:function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:true});t.default=void 0;var i={name:"QuestionRadio",props:{info:{type:Object,default:{question:null,explain:null,answer:null,types:"判断题"}},editable:{type:Boolean,default:false},readonly:{type:Boolean,default:false}},data:function e(){return{mouseOver:"",config:{message:null,theme:"error",offset:80},explainOpen:false,Question:JSON.parse(JSON.stringify(this.info)),rules:{question:[{required:true,message:"题目内容不能为空！",trigger:"blur"}],option:[{required:true,message:"选项内容不能为空！",trigger:"blur"}],answer:[{required:true,message:"答案不能为空",trigger:"blur"}],explain:[{required:true,message:"答案解析不能为空！",trigger:"blur"}]}}},computed:{optionStyle:function e(){var t=this;return function(e){if(t.Question.answer===e){return"choosed-style"}else if(t.mouseOver===e){return"mouseover-style"}else{return"option"}}}},created:function e(){if(this.Question.explain){this.explainOpen=true}},methods:{choose:function e(t){this.Question.answer=t},handleSwitcherChange:function e(t){if(!t&&!this.readonly){this.Question.explain=null}},checkData:function e(){var t=this;this.$refs.Question.validate().then(function(e){if(t.editable){t.$emit("updateQuestion",t.Question)}else{t.$emit("createQuestion",t.Question)}},function(e){t.config.message=e.content;t.config.theme="error";t.$bkMessage(t.config)})},reset:function e(){this.Question.question=null;this.Question.answer=null;this.Question.explain=null;this.explainOpen=false;this.$refs.Question.clearError()}}};t.default=i},118:function(e,t,n){},119:function(e,t,n){"use strict";n.r(t);var i=n(120);var o=n.n(i);for(var s in i)if(s!=="default")(function(e){n.d(t,e,function(){return i[e]})})(s);t["default"]=o.a},120:function(e,t,n){"use strict";var i=n(0);Object.defineProperty(t,"__esModule",{value:true});t.default=void 0;var o=i(n(81));var s={name:"QuestionShort",mixins:[o.default],props:{info:{type:Object,default:{question:null,answer:null,explain:null,types:"简答题"}}},data:function e(){return{}},created:function e(){},methods:{checkData:function e(){var t=this;this.$refs.Question.validate().then(function(e){if(t.editable){t.$emit("updateQuestion",t.Question)}else{t.$emit("createQuestion",t.Question)}},function(e){t.config.message=e.content;t.config.theme="error";t.$bkMessage(t.config)})},reset:function e(){this.Question.question=null;this.Question.answer=null;this.Question.explain=null;this.explainOpen=false;this.$refs.Question.clearError()}}};t.default=s},121:function(e,t,n){},122:function(e,t,n){"use strict";n.r(t);var i=n(123);var o=n.n(i);for(var s in i)if(s!=="default")(function(e){n.d(t,e,function(){return i[e]})})(s);t["default"]=o.a},123:function(e,t,n){"use strict";var i=n(0);Object.defineProperty(t,"__esModule",{value:true});t.default=void 0;var o=i(n(81));var s={name:"QuestionFill",mixins:[o.default],props:{info:{type:Object,default:{question:null,explain:null,answer:[],types:"填空题"}}},data:function e(){return{separator:" ",answer:[]}},computed:{},watch:{"Question.question":{handler:function e(t,n){if(t&&this.answer.length>0){var i=t.split("");var o=0;var s=1;for(var r=0;r<i.length-1;r++){if(i[r]==="_"&&i[r+1]==="_"){s=s+1;if(s===7){o=o+1}}else{if(s<7&&s>1){this.Question.question=n;this.handleClose(this.answer[o]);o=o+1}s=1}}if(s<7&&s>1){this.Question.question=n;this.handleClose(this.answer[o])}}},immediate:true}},created:function e(){if(this.editable||this.readonly){this.exchange()}if(this.Question.explain){this.explainOpen=true}},methods:{exchange:function e(){var t=this.Question.answer.split(this.separator);var n=this.Question.question.split("");for(var i=0;i<n.length-6;i++){if(n.slice(i,i+7).join("")==="_______"){var o=t.shift();this.answer.push({text:o,start:i,length:o.length});i=i+6}}},checkData:function e(){var t=this;if(!this.readonly){this.Question.answer=[]}this.answer.forEach(function(e){t.Question.answer.push(e.text)});this.$refs.Question.validate().then(function(e){t.Question.answer=t.Question.answer.join(t.separator);if(t.editable){t.$emit("updateQuestion",t.Question)}else{t.$emit("createQuestion",t.Question)}t.Question.answer=t.Question.answer.split(t.separator)},function(e){t.config.message=e.content;t.config.theme="error";t.$bkMessage(t.config)})},reset:function e(){this.Question.question=null;this.answer=[];this.Question.explain=null;this.explainOpen=false;this.$refs.Question.clearError()},handleMouseSelect:function e(){var t=window.getSelection().toString();var n=window.getSelection().anchorOffset;if(t&&t.indexOf("_")<0){this.answer.push({text:t,start:n,length:t.length});this.ascending_sort(this.answer,"start");this.answer.forEach(function(e){if(e.start>n){e.start=e.start+7-t.length}});var i=this.Question.question.split("");i.splice(n,t.length,"_______");this.Question.question=i.join("")}},handleClose:function e(t){var n=this.Question.question.split("");n.splice(t.start,7,t.text);this.answer.forEach(function(e){if(e.start>t.start){e.start=e.start+t.length-7;e.end=e.end+t.length-7}});this.Question.question=n.join("");this.answer.splice(this.answer.indexOf(t),1)},ascending_sort:function e(t,n){return t.sort(function(e,t){var i=e[n];var o=t[n];return i<o?-1:i>o?1:0})},handleSwitcherChange:function e(t){if(!t&&!this.readonly){this.Question.explain=null}}}};t.default=s},124:function(e,t,n){},141:function(e,t,n){"use strict";n.r(t);var i=n(185);var o=n(110);for(var s in o)if(s!=="default")(function(e){n.d(t,e,function(){return o[e]})})(s);var r=n(159);var a=n(2);var u=Object(a["a"])(o["default"],i["a"],i["b"],false,null,"4212c2b5",null);t["default"]=u.exports},142:function(e,t,n){"use strict";n.r(t);var i=n(186);var o=n(113);for(var s in o)if(s!=="default")(function(e){n.d(t,e,function(){return o[e]})})(s);var r=n(160);var a=n(2);var u=Object(a["a"])(o["default"],i["a"],i["b"],false,null,"faca7eba",null);t["default"]=u.exports},143:function(e,t,n){"use strict";n.r(t);var i=n(187);var o=n(116);for(var s in o)if(s!=="default")(function(e){n.d(t,e,function(){return o[e]})})(s);var r=n(161);var a=n(2);var u=Object(a["a"])(o["default"],i["a"],i["b"],false,null,"2984ed26",null);t["default"]=u.exports},144:function(e,t,n){"use strict";n.r(t);var i=n(188);var o=n(119);for(var s in o)if(s!=="default")(function(e){n.d(t,e,function(){return o[e]})})(s);var r=n(162);var a=n(2);var u=Object(a["a"])(o["default"],i["a"],i["b"],false,null,"5c6a1ceb",null);t["default"]=u.exports},145:function(e,t,n){"use strict";n.r(t);var i=n(189);var o=n(122);for(var s in o)if(s!=="default")(function(e){n.d(t,e,function(){return o[e]})})(s);var r=n(163);var a=n(2);var u=Object(a["a"])(o["default"],i["a"],i["b"],false,null,"12382b2f",null);t["default"]=u.exports},159:function(e,t,n){"use strict";var i=n(112);var o=n.n(i);var s=o.a},160:function(e,t,n){"use strict";var i=n(115);var o=n.n(i);var s=o.a},161:function(e,t,n){"use strict";var i=n(118);var o=n.n(i);var s=o.a},162:function(e,t,n){"use strict";var i=n(121);var o=n.n(i);var s=o.a},163:function(e,t,n){"use strict";var i=n(124);var o=n.n(i);var s=o.a},185:function(e,t,n){"use strict";var i=function(){var e=this;var t=e.$createElement;var n=e._self._c||t;return n("div",[n("bk-form",{ref:"Question",attrs:{model:e.Question,"label-width":0}},[n("div",{staticClass:"question"},[n("p",[e._v("题目:")]),e._v(" "),n("bk-form-item",{attrs:{required:true,rules:e.rules.question,property:"question","error-display-type":"normal"}},[n("bk-input",{staticStyle:{width:"84%"},attrs:{type:"textarea",readonly:e.readonly,autosize:{minRows:2,maxRows:2},placeholder:"请输入题目内容"},model:{value:e.Question.question,callback:function(t){e.$set(e.Question,"question",t)},expression:"Question.question"}})],1)],1),e._v(" "),n("div",{staticClass:"options"},[n("bk-form-item",{attrs:{required:true,rules:e.rules.answer,property:"answer","error-display-type":"normal"}},[n("bk-radio-group",{model:{value:e.Question.answer,callback:function(t){e.$set(e.Question,"answer",t)},expression:"Question.answer"}},[n("div",{class:e.optionStyle("A")},[n("bk-form-item",{attrs:{required:true,rules:e.rules.option,property:"option_A","icon-offset":20,"error-display-type":"tooltips"}},[n("bk-input",{ref:"optionA",staticStyle:{width:"100%"},attrs:{readonly:e.readonly,placeholder:"请输入选项A内容",size:"large"},on:{enter:function(t){e.nextOption("B")}},model:{value:e.Question.option_A,callback:function(t){e.$set(e.Question,"option_A",t)},expression:"Question.option_A"}},[n("template",{slot:"prepend"},[n("div",{staticClass:"group-text",on:{click:function(t){e.choose("A")},mouseover:function(t){e.mouseOver="A"},mouseleave:function(t){e.mouseOver=""}}},[n("label",[e._v("A")])])])],2)],1)],1),e._v(" "),n("div",{class:e.optionStyle("B")},[n("bk-form-item",{attrs:{required:true,rules:e.rules.option,property:"option_B","icon-offset":20}},[n("bk-input",{ref:"optionB",staticStyle:{width:"100%"},attrs:{readonly:e.readonly,placeholder:"请输入选项B内容",size:"large"},on:{enter:function(t){e.nextOption("C")}},model:{value:e.Question.option_B,callback:function(t){e.$set(e.Question,"option_B",t)},expression:"Question.option_B"}},[n("template",{slot:"prepend"},[n("div",{staticClass:"group-text",on:{click:function(t){e.choose("B")},mouseover:function(t){e.mouseOver="B"},mouseleave:function(t){e.mouseOver=""}}},[n("label",[e._v("B")])])])],2)],1)],1),e._v(" "),n("div",{class:e.optionStyle("C")},[n("bk-form-item",{attrs:{required:true,rules:e.rules.option,property:"option_C","icon-offset":20}},[n("bk-input",{ref:"optionC",staticStyle:{width:"100%"},attrs:{readonly:e.readonly,placeholder:"请输入选项C内容",size:"large"},on:{enter:function(t){e.nextOption("D")}},model:{value:e.Question.option_C,callback:function(t){e.$set(e.Question,"option_C",t)},expression:"Question.option_C"}},[n("template",{slot:"prepend"},[n("div",{staticClass:"group-text",on:{click:function(t){e.choose("C")},mouseover:function(t){e.mouseOver="C"},mouseleave:function(t){e.mouseOver=""}}},[n("label",[e._v("C")])])])],2)],1)],1),e._v(" "),n("div",{class:e.optionStyle("D")},[n("bk-form-item",{attrs:{required:true,rules:e.rules.option,property:"option_D","icon-offset":20}},[n("bk-input",{ref:"optionD",staticStyle:{width:"100%"},attrs:{readonly:e.readonly,placeholder:"请输入选项D内容",size:"large"},on:{enter:function(t){e.nextOption("A")}},model:{value:e.Question.option_D,callback:function(t){e.$set(e.Question,"option_D",t)},expression:"Question.option_D"}},[n("template",{slot:"prepend"},[n("div",{staticClass:"group-text",on:{click:function(t){e.choose("D")},mouseover:function(t){e.mouseOver="D"},mouseleave:function(t){e.mouseOver=""}}},[n("label",[e._v("D")])])])],2)],1)],1)])],1)],1),e._v(" "),n("div",{staticClass:"rightAnswer"},[n("p",[e._v("正确答案："+e._s(e.Question.answer))])]),e._v(" "),n("div",{staticClass:"analysis"},[n("bk-switcher",{attrs:{theme:"primary","show-text":true,"on-text":"解析","off-text":"解析"},on:{change:e.handleSwitcherChange},model:{value:e.explainOpen,callback:function(t){e.explainOpen=t},expression:"explainOpen"}}),e._v(" "),!e.readonly?n("bk-button",{staticClass:"reset",attrs:{theme:"primary"},on:{click:e.reset}},[e._v("重置")]):e._e(),e._v(" "),!e.readonly?n("bk-button",{staticClass:"upload",attrs:{theme:"primary"},on:{click:e.checkData}},[e._v("上传")]):e._e(),e._v(" "),e.explainOpen?n("bk-form-item",{attrs:{required:true,rules:e.rules.explain,property:"explain","error-display-type":"normal"}},[e.explainOpen?n("bk-input",{staticStyle:{width:"100%",display:"block","margin-top":"10px"},attrs:{type:"textarea",autosize:{minRows:2,maxRows:2},placeholder:"请输入答案解析内容"},model:{value:e.Question.explain,callback:function(t){e.$set(e.Question,"explain",t)},expression:"Question.explain"}}):e._e()],1):e._e()],1),e._v(" "),n("div",{staticClass:"upload"})])],1)};var o=[];n.d(t,"a",function(){return i});n.d(t,"b",function(){return o})},186:function(e,t,n){"use strict";var i=function(){var e=this;var t=e.$createElement;var n=e._self._c||t;return n("div",[n("bk-form",{ref:"Question",attrs:{model:e.Question,"label-width":0}},[n("div",{staticClass:"question"},[n("p",[e._v("题目:")]),e._v(" "),n("bk-form-item",{attrs:{required:true,rules:e.rules.question,property:"question","error-display-type":"normal"}},[n("bk-input",{staticStyle:{width:"84%"},attrs:{type:"textarea",readonly:e.readonly,autosize:{minRows:2,maxRows:2},placeholder:"请输入题目内容"},model:{value:e.Question.question,callback:function(t){e.$set(e.Question,"question",t)},expression:"Question.question"}})],1)],1),e._v(" "),n("div",{staticClass:"options"},[n("bk-form-item",{attrs:{required:true,rules:e.rules.answer,property:"answer","error-display-type":"normal"}},[n("bk-radio-group",{model:{value:e.Question.answer,callback:function(t){e.$set(e.Question,"answer",t)},expression:"Question.answer"}},[n("div",{class:e.optionStyle("A")},[n("bk-form-item",{attrs:{required:true,rules:e.rules.option,property:"option_A","icon-offset":20,"error-display-type":"tooltips"}},[n("bk-input",{ref:"optionA",staticStyle:{width:"100%"},attrs:{readonly:e.readonly,placeholder:"请输入选项A内容",size:"large"},on:{enter:function(t){e.nextOption("B")}},model:{value:e.Question.option_A,callback:function(t){e.$set(e.Question,"option_A",t)},expression:"Question.option_A"}},[n("template",{slot:"prepend"},[n("div",{staticClass:"group-text",on:{click:function(t){e.choose("A")},mouseover:function(t){e.mouseOver="A"},mouseleave:function(t){e.mouseOver=""}}},[n("label",[e._v("A")])])])],2)],1)],1),e._v(" "),n("div",{class:e.optionStyle("B")},[n("bk-form-item",{attrs:{required:true,rules:e.rules.option,property:"option_B","icon-offset":20,"error-display-type":"tooltips"}},[n("bk-input",{ref:"optionB",staticStyle:{width:"100%"},attrs:{readonly:e.readonly,placeholder:"请输入选项B内容",size:"large"},on:{enter:function(t){e.nextOption("C")}},model:{value:e.Question.option_B,callback:function(t){e.$set(e.Question,"option_B",t)},expression:"Question.option_B"}},[n("template",{slot:"prepend"},[n("div",{staticClass:"group-text",on:{click:function(t){e.choose("B")},mouseover:function(t){e.mouseOver="B"},mouseleave:function(t){e.mouseOver=""}}},[n("label",[e._v("B")])])])],2)],1)],1),e._v(" "),n("div",{class:e.optionStyle("C")},[n("bk-form-item",{attrs:{required:true,rules:e.rules.option,property:"option_C","icon-offset":20,"error-display-type":"tooltips"}},[n("bk-input",{ref:"optionC",staticStyle:{width:"100%"},attrs:{readonly:e.readonly,placeholder:"请输入选项C内容",size:"large"},on:{enter:function(t){e.nextOption("D")}},model:{value:e.Question.option_C,callback:function(t){e.$set(e.Question,"option_C",t)},expression:"Question.option_C"}},[n("template",{slot:"prepend"},[n("div",{staticClass:"group-text",on:{click:function(t){e.choose("C")},mouseover:function(t){e.mouseOver="C"},mouseleave:function(t){e.mouseOver=""}}},[n("label",[e._v("C")])])])],2)],1)],1),e._v(" "),n("div",{class:e.optionStyle("D")},[n("bk-form-item",{attrs:{required:true,rules:e.rules.option,property:"option_D","icon-offset":20,"error-display-type":"tooltips"}},[n("bk-input",{ref:"optionD",staticStyle:{width:"100%"},attrs:{readonly:e.readonly,placeholder:"请输入选项D内容",size:"large"},on:{enter:function(t){e.nextOption("E")}},model:{value:e.Question.option_D,callback:function(t){e.$set(e.Question,"option_D",t)},expression:"Question.option_D"}},[n("template",{slot:"prepend"},[n("div",{staticClass:"group-text",on:{click:function(t){e.choose("D")},mouseover:function(t){e.mouseOver="D"},mouseleave:function(t){e.mouseOver=""}}},[n("label",[e._v("D")])])])],2)],1)],1),e._v(" "),n("div",{class:e.optionStyle("E")},[n("bk-form-item",{attrs:{required:true,rules:e.rules.option,property:"option_E","icon-offset":20,"error-display-type":"tooltips"}},[n("bk-input",{ref:"optionE",staticStyle:{width:"100%"},attrs:{readonly:e.readonly,placeholder:"请输入选项E内容",size:"large"},on:{enter:function(t){e.nextOption("A")}},model:{value:e.Question.option_E,callback:function(t){e.$set(e.Question,"option_E",t)},expression:"Question.option_E"}},[n("template",{slot:"prepend"},[n("div",{staticClass:"group-text",on:{click:function(t){e.choose("E")},mouseover:function(t){e.mouseOver="E"},mouseleave:function(t){e.mouseOver=""}}},[n("label",[e._v("E")])])])],2)],1)],1)])],1)],1),e._v(" "),n("div",{staticClass:"rightAnswer"},[e._v("\n            正确答案：\n            "),e._l(e.Question.answer,function(t){return n("p",{key:t,staticStyle:{display:"inline-block","margin-right":"5px"}},[e._v(e._s(t))])})],2),e._v(" "),n("div",{staticClass:"analysis"},[n("bk-switcher",{attrs:{theme:"primary","show-text":true,"on-text":"解析","off-text":"解析"},on:{change:e.handleSwitcherChange},model:{value:e.explainOpen,callback:function(t){e.explainOpen=t},expression:"explainOpen"}}),e._v(" "),!e.readonly?n("bk-button",{staticClass:"reset",attrs:{theme:"primary"},on:{click:e.reset}},[e._v("重置")]):e._e(),e._v(" "),!e.readonly?n("bk-button",{staticClass:"upload",attrs:{theme:"primary"},on:{click:e.checkData}},[e._v("上传")]):e._e(),e._v(" "),e.explainOpen?n("bk-form-item",{attrs:{required:true,rules:e.rules.explain,property:"explain","error-display-type":"normal"}},[e.explainOpen?n("bk-input",{staticStyle:{width:"100%",display:"block","margin-top":"10px"},attrs:{type:"textarea",autosize:{minRows:2,maxRows:2},placeholder:"请输入答案解析内容"},model:{value:e.Question.explain,callback:function(t){e.$set(e.Question,"explain",t)},expression:"Question.explain"}}):e._e()],1):e._e()],1)])],1)};var o=[];n.d(t,"a",function(){return i});n.d(t,"b",function(){return o})},187:function(e,t,n){"use strict";var i=function(){var e=this;var t=e.$createElement;var n=e._self._c||t;return n("div",[n("bk-form",{ref:"Question",attrs:{model:e.Question,"label-width":0}},[n("div",{staticClass:"question"},[n("p",[e._v("题目:")]),e._v(" "),n("bk-form-item",{attrs:{required:true,rules:e.rules.question,property:"question","error-display-type":"normal"}},[n("bk-input",{staticStyle:{width:"84%"},attrs:{type:"textarea",autosize:{minRows:2,maxRows:2},readonly:e.readonly,placeholder:"请输入题目内容"},model:{value:e.Question.question,callback:function(t){e.$set(e.Question,"question",t)},expression:"Question.question"}})],1)],1),e._v(" "),!e.readonly?n("div",{staticClass:"options"},[n("bk-form-item",{attrs:{required:true,rules:e.rules.answer,property:"answer","error-display-type":"normal"}},[n("bk-radio-group",{model:{value:e.Question.answer,callback:function(t){e.$set(e.Question,"answer",t)},expression:"Question.answer"}},[n("div",{class:e.optionStyle("true"),on:{click:function(t){e.choose("true")},mouseover:function(t){e.mouseOver="true"},mouseleave:function(t){e.mouseOver=""}}},[n("bk-radio",{staticStyle:{"margin-top":"38px","margin-left":"10px"},attrs:{name:"T",value:"true"}},[e._v("\n                            正确\n                        ")])],1),e._v(" "),n("div",{class:e.optionStyle("false"),on:{click:function(t){e.choose("false")},mouseover:function(t){e.mouseOver="false"},mouseleave:function(t){e.mouseOver=""}}},[n("bk-radio",{staticStyle:{"margin-top":"38px","margin-left":"10px"},attrs:{name:"F",value:"false"}},[e._v("\n                            错误\n                        ")])],1)])],1)],1):e._e(),e._v(" "),n("div",{staticClass:"rightAnswer"},[n("p",[e._v("正确答案："+e._s(e.Question.answer==="true"?"正确":"错误"))])]),e._v(" "),n("div",{staticClass:"analysis"},[n("bk-switcher",{attrs:{theme:"primary","show-text":true,"on-text":"解析","off-text":"解析"},on:{change:e.handleSwitcherChange},model:{value:e.explainOpen,callback:function(t){e.explainOpen=t},expression:"explainOpen"}}),e._v(" "),!e.readonly?n("bk-button",{staticClass:"reset",attrs:{theme:"primary"},on:{click:e.reset}},[e._v("重置")]):e._e(),e._v(" "),!e.readonly?n("bk-button",{staticClass:"upload",attrs:{theme:"primary"},on:{click:e.checkData}},[e._v("上传")]):e._e(),e._v(" "),e.explainOpen?n("bk-form-item",{attrs:{required:true,rules:e.rules.explain,property:"explain","error-display-type":"normal"}},[e.explainOpen?n("bk-input",{staticStyle:{width:"100%",display:"block","margin-top":"10px"},attrs:{type:"textarea",autosize:{minRows:2,maxRows:2},readonly:e.readonly,placeholder:"请输入答案解析内容"},model:{value:e.Question.explain,callback:function(t){e.$set(e.Question,"explain",t)},expression:"Question.explain"}}):e._e()],1):e._e()],1)])],1)};var o=[];n.d(t,"a",function(){return i});n.d(t,"b",function(){return o})},188:function(e,t,n){"use strict";var i=function(){var e=this;var t=e.$createElement;var n=e._self._c||t;return n("div",[n("bk-form",{ref:"Question",attrs:{model:e.Question,"label-width":0}},[n("div",{staticClass:"question"},[n("p",[e._v("题目:")]),e._v(" "),n("bk-form-item",{attrs:{required:true,rules:e.rules.question,property:"question","error-display-type":"normal"}},[n("bk-input",{staticStyle:{width:"84%"},attrs:{type:"textarea",autosize:{minRows:4,maxRows:4},readonly:e.readonly,placeholder:"请输入题目内容"},model:{value:e.Question.question,callback:function(t){e.$set(e.Question,"question",t)},expression:"Question.question"}})],1)],1),e._v(" "),n("div",{staticClass:"rightAnswer"},[n("p",[e._v("正确答案:")]),e._v(" "),n("bk-form-item",{attrs:{required:true,rules:e.rules.answer,property:"answer","error-display-type":"normal"}},[n("bk-input",{staticStyle:{width:"84%"},attrs:{type:"textarea",autosize:{minRows:4,maxRows:4},readonly:e.readonly,placeholder:"请输入正确答案内容"},model:{value:e.Question.answer,callback:function(t){e.$set(e.Question,"answer",t)},expression:"Question.answer"}})],1)],1),e._v(" "),n("div",{staticClass:"analysis"},[n("bk-switcher",{attrs:{theme:"primary","show-text":true,"on-text":"解析","off-text":"解析"},on:{change:e.handleSwitcherChange},model:{value:e.explainOpen,callback:function(t){e.explainOpen=t},expression:"explainOpen"}}),e._v(" "),!e.readonly?n("bk-button",{staticClass:"reset",attrs:{theme:"primary"},on:{click:e.reset}},[e._v("重置")]):e._e(),e._v(" "),!e.readonly?n("bk-button",{staticClass:"upload",attrs:{theme:"primary"},on:{click:e.checkData}},[e._v("上传")]):e._e(),e._v(" "),e.explainOpen?n("bk-form-item",{attrs:{required:true,rules:e.rules.explain,property:"explain","error-display-type":"normal"}},[e.explainOpen?n("bk-input",{staticStyle:{width:"100%",display:"block","margin-top":"10px"},attrs:{type:"textarea",autosize:{minRows:2,maxRows:2},readonly:e.readonly,placeholder:"请输入答案解析内容"},model:{value:e.Question.explain,callback:function(t){e.$set(e.Question,"explain",t)},expression:"Question.explain"}}):e._e()],1):e._e()],1)])],1)};var o=[];n.d(t,"a",function(){return i});n.d(t,"b",function(){return o})},189:function(e,t,n){"use strict";var i=function(){var e=this;var t=e.$createElement;var n=e._self._c||t;return n("div",[n("bk-form",{ref:"Question",attrs:{model:e.Question,"label-width":0}},[n("div",{staticClass:"question"},[n("p",[e._v("题目:")]),e._v(" "),n("div",{staticClass:"question1"},[n("bk-form-item",{attrs:{required:true,rules:e.rules.question,property:"question","error-display-type":"normal"}},[n("bk-input",{staticStyle:{width:"84%"},attrs:{type:"textarea",readonly:e.readonly,autosize:{minRows:2,maxRows:2},placeholder:"请输入题目内容"},model:{value:e.Question.question,callback:function(t){e.$set(e.Question,"question",t)},expression:"Question.question"}})],1)],1),e._v(" "),!e.readonly?n("p",[e._v("用鼠标选中下列文本的内容进行挖空:")]):e._e(),e._v(" "),n("bk-form-item",{attrs:{required:true,rules:e.rules.answer,property:"answer","error-display-type":"normal"}},[!e.readonly?n("div",{staticClass:"hollow"},[n("label",{staticStyle:{display:"block"},on:{mouseup:e.handleMouseSelect}},[e._v(e._s(e.Question.question))])]):e._e()])],1),e._v(" "),n("div",{staticClass:"rightAnswer"},[n("p",{staticStyle:{display:"inline-block"}},[e._v("正确答案:")]),e._v(" "),e._l(e.answer,function(t,i){return n("bk-tag",{key:t,staticStyle:{display:"inline-block"},attrs:{theme:"info",closable:!e.readonly,"disable-transitions":false},on:{close:function(n){e.handleClose(t)}}},[e._v("\n                "+e._s("填空"+(i+1)+":"+t.text)+"\n            ")])})],2),e._v(" "),n("div",{staticClass:"analysis"},[n("bk-switcher",{attrs:{theme:"primary","show-text":true,"on-text":"解析","off-text":"解析"},on:{change:e.handleSwitcherChange},model:{value:e.explainOpen,callback:function(t){e.explainOpen=t},expression:"explainOpen"}}),e._v(" "),!e.readonly?n("bk-button",{staticClass:"reset",attrs:{theme:"primary"},on:{click:e.reset}},[e._v("重置")]):e._e(),e._v(" "),!e.readonly?n("bk-button",{staticClass:"upload",attrs:{theme:"primary"},on:{click:e.checkData}},[e._v("上传")]):e._e(),e._v(" "),e.explainOpen?n("bk-form-item",{attrs:{required:true,rules:e.rules.explain,property:"explain","error-display-type":"normal"}},[e.explainOpen?n("bk-input",{staticStyle:{width:"100%",display:"block","margin-top":"10px"},attrs:{type:"textarea",autosize:{minRows:2,maxRows:2},placeholder:"请输入答案解析内容"},model:{value:e.Question.explain,callback:function(t){e.$set(e.Question,"explain",t)},expression:"Question.explain"}}):e._e()],1):e._e()],1)])],1)};var o=[];n.d(t,"a",function(){return i});n.d(t,"b",function(){return o})},81:function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:true});t.default=void 0;var i={props:{editable:{type:Boolean,default:false},readonly:{type:Boolean,default:false}},data:function e(){return{mouseOver:"",config:{message:null,theme:"error",offset:80},Question:JSON.parse(JSON.stringify(this.info)),explainOpen:false,rules:{question:[{required:true,message:"题目内容不能为空",trigger:"change"}],option:[{required:true,message:"选项内容不能为空",trigger:"change"}],answer:[{required:true,message:"答案不能为空",trigger:"change"}],explain:[{required:true,message:"答案解析不能为空",trigger:"change"}]}}},created:function e(){if(this.Question.explain){this.explainOpen=true}},methods:{checkData:function e(){var t=this;this.$refs.Question.validate().then(function(e){if(t.editable){t.$emit("updateQuestion",t.Question)}else{t.$emit("createQuestion",t.Question)}},function(e){t.config.message=e.content;t.config.theme="error";t.$bkMessage(t.config)})},handleSwitcherChange:function e(t){if(!t&&!this.readonly){this.Question.explain=null}}}};t.default=i}}]);