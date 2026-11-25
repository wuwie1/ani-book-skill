// 图幅坐标以西北角为原点。区域是读图分区，点位供排图使用。
export const regions = [
  {
    id: 'shuo', name: '朔河州', kind: '北境河谷', anchor: [.436, .246], crop: [47, 34], color: '#788b69',
    summary: '朔河从靖原城外流过。船到分舟口，往临川的货要换浅底驳船，留在干流上的粮船则一路向七港去。',
    passage: '靖原城至南渡仓约一时辰。自仓顺水到回澜渡约半日，改走陆路到石梁哨需一日。', sheet: 'journey'
  },
  {
    id: 'steppe', name: '北荒', kind: '草甸与林缘', anchor: [.455, .095], crop: [65, 15], color: '#b49c64',
    summary: '草原在图幅以北继续延伸。逐水诸部各有首领，乌铎所在的迁徙队沿水草往返，营地随季节移动。',
    passage: '春日给母畜留饮水道，重车绕行硬地。秋草落籽之后，回青甸才可开市。', sheet: 'trade'
  },
  {
    id: 'west', name: '玄朔矿区', kind: '西部山地', anchor: [.12, .415], crop: [11, 53], color: '#a48158',
    summary: '玄朔帝国掌西部矿山。矿料从东麓出山，在山前过秤，再交给往大周北境去的脚户。',
    passage: '两边脚户各领一程运钱。遇上湿矿，在哪一边晾干、在哪一边称重，会改动整批货的价钱。', sheet: 'trade'
  },
  {
    id: 'central', name: '大周中原', kind: '平原与王都', anchor: [.335, .616], crop: [42, 73], color: '#bca677',
    summary: '北境以南，田畴间的道路通向承京。朝廷的诏令从王都发出，再由北边的军府、渡仓和地方官署接办。',
    passage: '王都设官署、太学和神宫。此图取大周仍在的开篇时点，陆昊尚未获授临川试治。', sheet: 'trade'
  },
  {
    id: 'east', name: '东部山地', kind: '林谷与炉山', anchor: [.84, .31], crop: [89, 23], color: '#648570',
    summary: '北境往东南，林谷渐入岩山。灵狐族守药圃与祖地，赤炉魔城靠火脉炼器，万妖坊盟的匠铺散在山口。',
    passage: '两渠堰的一支水入药圃，另一支供炉户使用。旱季的取水时段由双方在堰边议定。', sheet: 'trade'
  },
  {
    id: 'ports', name: '七港河口', kind: '河口港群', anchor: [.716, .678], crop: [76, 71], color: '#b58a60',
    summary: '朔河下游在这里入海。七处泊地分办过秤、卸粮、拼货、补水、候潮、修船和避风，共用一张靠泊单。',
    passage: '近岸旧路可进背风澳。拟勘的外礁线从潮生坞出海，经听风屿换领航人，还须约妥回航泊位。', sheet: 'harbors'
  },
  {
    id: 'sea', name: '东南海疆', kind: '近海与潮路', anchor: [.689, .916], crop: [72, 89], color: '#568982',
    summary: '出七港便见东南海疆。水下潮路要请氐人领航，龙族水府的水脉另有主人，通行须分别议定。',
    passage: '七港以外的海面仍在武元界内。跨往别界须另核通天渡两端阵基、坐标、供能、界潮窗口与返程余量。', sheet: 'harbors'
  },
  {
    id: 'isles', name: '羽民岛聚', kind: '外海群岛', anchor: [.927, .924], crop: [93, 88], color: '#798e72',
    summary: '七港之外散布羽民聚居的海岛。岛上人立风标、记海雾，氐人领潮人熟悉礁间的水路。',
    passage: '听风屿的水只够守岛人和遇险船。走外礁的商船须先在青瓮浦装足淡水，再约风信与进出潮时。', sheet: 'harbors'
  }
];

// 地标的归属只表示图上的地理分组。
export const places = [
  { id: 'jing', name: '靖原城', region: 'shuo', kind: '城邑', at: [.472, .335], major: true, city: 1, info: '淮北王府驻地。边军、医署和教习都在城中，陆昊自这里沿着凭单去南渡仓找船。' },
  { id: 'lin', name: '临川城', region: 'shuo', kind: '城邑', at: [.643, .363], major: true, city: .75, info: '城边旧渡在朔河支流上游，连着荒矿、旧炉与农田。卷一末陆昊获试治机会，卷二才赴任接收。' },
  { id: 'depot', name: '南渡仓', region: 'shuo', kind: '仓渡', at: [.492, .365], info: '从靖原约一时辰到仓。此处凭单交接，去回澜渡的水路和去石梁哨的陆路在这里分开。' },
  { id: 'ferry', name: '回澜渡', region: 'shuo', kind: '渡口', at: [.545, .418], info: '由南渡仓顺水约半日，货船在此靠泊换手。逆水回程另算。' },
  { id: 'post', name: '石梁哨', region: 'shuo', kind: '哨所', at: [.395, .406], info: '从南渡仓走陆路需一日。驿骑在当晚值夜前送达，陆昊随护卫次日抵哨，第六章补上第二夜的灯。' },
  { id: 'fork', name: '分舟口', region: 'shuo', kind: '汇流口', at: [.585, .493], draft: true, info: '干支两水交汇，深腹粮船在外汊卸货，浅底驳船转入临川支流。靖原赴临川的三日货船拟期已计入换载。' },
  { id: 'meadow', name: '回青甸', region: 'steppe', kind: '季节牧场', at: [.593, .152], draft: true, info: '靖原以北的林缘浅洼。雪退时牧户带产仔的母畜来吃头茬青，入秋可用皮毡、驮畜换盐粮。' },
  { id: 'quarry', name: '界石场', region: 'west', kind: '矿市', at: [.224, .371], draft: true, info: '玄朔矿区东麓的山前交易地。矿商在西验石，大周买家在东过秤。' },
  { id: 'capital', name: '承京', region: 'central', kind: '王都', at: [.419, .717], major: true, city: 1.3, info: '大周王都，坐落在中原腹地。王权、官署、太学与神宫集中于此。' },
  { id: 'court', name: '灵狐族圣庭', region: 'east', kind: '山门', at: [.859, .21], city: .65, info: '林谷中的祖地与药圃。守山与外通各有主张，陆昊的母族联系为他提供入山的机会。' },
  { id: 'forge', name: '赤炉魔城', region: 'east', kind: '炉城', at: [.891, .497], city: .7, info: '东南岩山间的炉城，靠火脉、矿料与炼器师承维持工造。炉契和维护决定能接下多少活。' },
  { id: 'weir', name: '两渠堰', region: 'east', kind: '水堰', at: [.726, .281], draft: true, info: '临川上游的山溪在此分水，一渠入灵狐药圃，一渠供炉户水轮与冷却池。山口匠铺收修轮轴。' },
  { id: 'weigh', name: '芦秤埠', region: 'ports', kind: '过秤泊地', at: [.675, .624], draft: true, info: '入港的河船先在这里过秤，再安排卸货。' },
  { id: 'grain', name: '石廒港', region: 'ports', kind: '粮仓', at: [.679, .667], draft: true, info: '粮船在此卸仓。逆风滞港时，粮行仍须按天付仓钱。' },
  { id: 'shift', name: '双桅泊', region: 'ports', kind: '换班泊地', at: [.712, .643], draft: true, info: '船队在这里拼货换班，再分头转运。' },
  { id: 'water', name: '青瓮浦', region: 'ports', kind: '淡水泊地', at: [.697, .701], draft: true, info: '出海船在这里装淡水，走外礁前须备足往返用水。' },
  { id: 'tide', name: '白蛎湾', region: 'ports', kind: '候潮湾', at: [.749, .652], draft: true, info: '近岸旧路上的浅湾，浅底船可以在这里候潮。' },
  { id: 'dock', name: '潮生坞', region: 'ports', kind: '修船坞', at: [.735, .713], draft: true, info: '河口内侧的斜船台依潮排期。木料与临川铁件在此装船，坞中师傅负责修船配舵。' },
  { id: 'shelter', name: '背风澳', region: 'ports', kind: '避风泊地', at: [.782, .682], draft: true, info: '航船在风暴中进澳避泊，连日逆风时须先给船工留床位。' },
  { id: 'wind', name: '听风屿', region: 'isles', kind: '领航岛屿', at: [.821, .846], draft: true, info: '羽民岛聚西北缘的小岛，守岛人测风、记雾，外礁线的商船在这里换领航人。' }
];

export const routes = [
  { id: 'depot-road', from: 'jing', to: 'depot', kind: 'land', time: '约一时辰', path: [[.485, .347]] },
  { id: 'post-road', from: 'depot', to: 'post', kind: 'land', time: '陆路一日', path: [[.467, .39], [.433, .385]] },
  { id: 'ferry-run', from: 'depot', to: 'ferry', kind: 'river', time: '顺水约半日', path: [[.525, .373], [.55, .398]] },
  { id: 'inshore', from: 'dock', to: 'shelter', kind: 'sea', time: '近岸旧路', path: [[.765, .731], [.794, .709]] },
  { id: 'outer', from: 'dock', to: 'wind', kind: 'planned', time: '外礁候选线', path: [[.772, .757], [.789, .811]] }
];

export const regionById = Object.fromEntries(regions.map(item => [item.id, item]));
export const placeById = Object.fromEntries(places.map(item => [item.id, item]));
