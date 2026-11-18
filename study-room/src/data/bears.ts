// 陪学熊的人设配置
// 每只熊有 5 种表情，对应自习的不同状态
export type BearId = 'chenggong' | 'xutang' | 'xiaolin' | 'xiaozhao' | 'laozhou'

// 自习状态：待机 / 专注中 / 暂停 / 完成
export type Mood = 'idle' | 'running' | 'paused' | 'done'

export interface Bear {
  id: BearId
  name: string       // 显示名字
  style: string      // 学习人设标签
  desc: string       // 一句话介绍
  lines: Record<Mood, string>  // 各状态下说的话
}

// 表情文件对应关系：mood -> 图片后缀
export const moodToEmotion: Record<Mood, string> = {
  idle: 'natural',    // 待机：自然
  running: 'serious', // 专注中：认真
  paused: 'helpless', // 暂停：无奈
  done: 'happy',      // 完成：开心
}

export const bears: Bear[] = [
  {
    id: 'chenggong',
    name: '陈工',
    style: '严格监督型',
    desc: '戴眼镜的严谨前辈，绝不允许你走神。',
    lines: {
      idle: '时间就是生命，选定目标就开始。',
      running: '别走神，专注当下这一件事。',
      paused: '暂停可以，但别停太久。',
      done: '不错，这一轮没有偷懒。',
    },
  },
  {
    id: 'xutang',
    name: '许棠',
    style: '温柔陪读型',
    desc: '抱着书的温柔同伴，慢慢来也不催你。',
    lines: {
      idle: '找个舒服的姿势，我们慢慢开始。',
      running: '别急，我在这儿陪着你。',
      paused: '累了就歇会儿，没关系的。',
      done: '你看，你真的做到了。',
    },
  },
  {
    id: 'xiaolin',
    name: '小林',
    style: '元气打气型',
    desc: '永远精神满满，举手给你加油。',
    lines: {
      idle: '准备好啦？我们开工吧！',
      running: '冲呀！这一轮一定行！',
      paused: '休息一下，马上满血复活！',
      done: '太棒啦！你超厉害的！',
    },
  },
  {
    id: 'xiaozhao',
    name: '小赵',
    style: '卷王冲刺型',
    desc: '握拳冲刺的进取派，带你一起卷。',
    lines: {
      idle: '磨刀不误砍柴工，定好就冲。',
      running: '稳住，坚持到最后！',
      paused: '休息是为了跑得更快，快回来。',
      done: '漂亮！又超 plan 了。',
    },
  },
  {
    id: 'laozhou',
    name: '老周',
    style: '佛系淡定型',
    desc: '扶眼镜的老大哥，淡定地陪你耗。',
    lines: {
      idle: '急什么，坐下来，学一点是一点。',
      running: '心静自然凉，慢慢来。',
      paused: '歇会儿也好，别有负担。',
      done: '嗯，挺好，有进步。',
    },
  },
]

// 根据熊 id 和状态拿到立绘路径
export function getBearImage(id: BearId, mood: Mood): string {
  return `/bears/${id}-${moodToEmotion[mood]}.png`
}

// 根据 id 找到熊的配置
export function findBear(id: BearId): Bear {
  return bears.find((b) => b.id === id) ?? bears[0]
}
