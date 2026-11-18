// 自习记录：一条记录 = 一次完成的专注
export interface StudyRecord {
  date: string      // 日期，格式 YYYY-MM-DD
  minutes: number   // 专注时长（分钟）
  bear: string      // 陪学熊的 id
}

const STORAGE_KEY = 'xiaoxiong-study-records'

// 读取所有记录。读不到或格式不对就返回空数组
export function loadRecords(): StudyRecord[] {
  try {
    const text = localStorage.getItem(STORAGE_KEY)
    if (!text) return []
    const data = JSON.parse(text)
    if (!Array.isArray(data)) return []
    return data
  } catch {
    return []
  }
}

// 保存全部记录
export function saveRecords(records: StudyRecord[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records))
}

// 追加一条记录
export function addRecord(record: StudyRecord): StudyRecord[] {
  const records = loadRecords()
  records.push(record)
  saveRecords(records)
  return records
}

// 拿到本地日期 YYYY-MM-DD
export function todayString(): string {
  const d = new Date()
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 统计结果
export interface Stats {
  totalMinutes: number   // 累计专注分钟
  totalSessions: number  // 累计完成次数
  studyDays: number      // 打卡天数
  streak: number         // 连续打卡天数
  last7: { label: string; minutes: number }[]  // 最近 7 天
}

// 计算统计数据
export function calcStats(records: StudyRecord[]): Stats {
  let totalMinutes = 0
  const dayMinutes: Record<string, number> = {}

  for (const r of records) {
    totalMinutes += r.minutes
    if (dayMinutes[r.date] === undefined) {
      dayMinutes[r.date] = 0
    }
    dayMinutes[r.date] += r.minutes
  }

  const studyDays = Object.keys(dayMinutes).length

  // 连续打卡天数：从今天往前数，断了就停
  let streak = 0
  const cursor = new Date()
  while (true) {
    const y = cursor.getFullYear()
    const m = String(cursor.getMonth() + 1).padStart(2, '0')
    const d = String(cursor.getDate()).padStart(2, '0')
    const key = `${y}-${m}-${d}`
    if (dayMinutes[key] !== undefined) {
      streak += 1
      cursor.setDate(cursor.getDate() - 1)
    } else {
      break
    }
  }

  // 最近 7 天
  const last7: { label: string; minutes: number }[] = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    last7.push({
      label: `${d.getMonth() + 1}/${d.getDate()}`,
      minutes: dayMinutes[key] ?? 0,
    })
  }

  return {
    totalMinutes,
    totalSessions: records.length,
    studyDays,
    streak,
    last7,
  }
}
