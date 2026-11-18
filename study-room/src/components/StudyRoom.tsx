import { useEffect, useRef, useState } from 'react'
import { findBear, getBearImage, type BearId, type Mood } from '../data/bears'
import { addRecord, todayString } from '../data/storage'

interface Props {
  bearId: BearId
  onBack: () => void
  onFinish: (minutes: number) => void
}

type Phase = 'setup' | 'running' | 'paused'

export default function StudyRoom({ bearId, onBack, onFinish }: Props) {
  const bear = findBear(bearId)

  const [minutes, setMinutes] = useState(25)
  const [phase, setPhase] = useState<Phase>('setup')
  const [secondsLeft, setSecondsLeft] = useState(25 * 60)
  const timerRef = useRef<number | null>(null)

  // 状态对应的熊表情和台词
  const mood: Mood =
    phase === 'setup' ? 'idle' :
    phase === 'running' ? 'running' :
    phase === 'paused' ? 'paused' : 'done'

  // 计时逻辑
  useEffect(() => {
    if (phase !== 'running') return
    timerRef.current = window.setInterval(() => {
      setSecondsLeft((s) => {
        if (s <= 1) {
          return 0
        }
        return s - 1
      })
    }, 1000)
    return () => {
      if (timerRef.current !== null) {
        window.clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [phase])

  // 时间到 0，结束并打卡
  useEffect(() => {
    if (secondsLeft === 0 && phase === 'running') {
      setPhase('setup')
      addRecord({ date: todayString(), minutes, bear: bearId })
      onFinish(minutes)
    }
  }, [secondsLeft, phase, minutes, bearId, onFinish])

  // 选时长
  function chooseMinutes(m: number) {
    setMinutes(m)
    setSecondsLeft(m * 60)
  }

  // 开始
  function start() {
    setSecondsLeft(minutes * 60)
    setPhase('running')
  }

  // 暂停 / 继续
  function togglePause() {
    if (phase === 'running') setPhase('paused')
    else if (phase === 'paused') setPhase('running')
  }

  // 提前结束（完成已专注的部分）
  function endEarly() {
    const doneMinutes = Math.max(1, Math.round((minutes * 60 - secondsLeft) / 60))
    setPhase('setup')
    if (doneMinutes > 0) {
      addRecord({ date: todayString(), minutes: doneMinutes, bear: bearId })
    }
    onFinish(doneMinutes)
  }

  // 格式化时间
  const m = String(Math.floor(secondsLeft / 60)).padStart(2, '0')
  const s = String(secondsLeft % 60).padStart(2, '0')

  return (
    <div
      className="page study-page"
      style={{ backgroundImage: 'url(/bg/library.png)' }}
    >
      <div className="study-mask">
        <header className="topbar">
          <button className="link-btn" onClick={onBack}>← 换一只熊</button>
          <div className="brand">
            <span className="brand-mark">熊</span>
            <span>小熊自习室</span>
          </div>
          <div className="companion-tag">陪学伙伴：{bear.name}</div>
        </header>

        <main className="study-main">
          <div className="companion">
            <img
              className={'companion-img ' + (phase === 'running' ? 'breathing' : '')}
              src={getBearImage(bearId, mood)}
              alt={bear.name}
            />
            <div className="speech">
              <span className="speech-name">{bear.name}</span>
              <span className="speech-text">{bear.lines[mood]}</span>
            </div>
          </div>

          <div className="timer-card">
            {phase === 'setup' && (
              <div className="duration-picker">
                <div className="picker-label">这一段想专注多久？</div>
                <div className="duration-options">
                  {[15, 25, 45, 60].map((opt) => (
                    <button
                      key={opt}
                      className={'duration-opt ' + (minutes === opt ? 'active' : '')}
                      onClick={() => chooseMinutes(opt)}
                    >
                      {opt}<span>分钟</span>
                    </button>
                  ))}
                </div>
                <button className="primary-btn" onClick={start}>开始专注</button>
              </div>
            )}

            {phase !== 'setup' && (
              <div className="timer-running">
                <div className="timer-label">
                  {phase === 'running' ? '专注中 · 加油' : '已暂停 · 歇口气'}
                </div>
                <div className="timer-digits">{m}:{s}</div>
                <div className="timer-progress">
                  <div
                    className="timer-progress-fill"
                    style={{ width: `${((minutes * 60 - secondsLeft) / (minutes * 60)) * 100}%` }}
                  />
                </div>
                <div className="timer-actions">
                  <button className="secondary-btn" onClick={togglePause}>
                    {phase === 'running' ? '暂停' : '继续'}
                  </button>
                  <button className="ghost-btn" onClick={endEarly}>提前结束</button>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
