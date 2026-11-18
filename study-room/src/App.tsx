import { useState } from 'react'
import SelectBear from './components/SelectBear'
import StudyRoom from './components/StudyRoom'
import Complete from './components/Complete'
import Stats from './components/Stats'
import type { BearId } from './data/bears'

// 页面类型
type Screen = 'select' | 'study' | 'complete' | 'stats'

export default function App() {
  const [screen, setScreen] = useState<Screen>('select')
  const [bearId, setBearId] = useState<BearId>('chenggong')
  const [lastMinutes, setLastMinutes] = useState(0)

  // 选好熊，进入自习
  function handleSelect(id: BearId) {
    setBearId(id)
    setScreen('study')
  }

  // 自习完成，进入打卡页
  function handleFinish(minutes: number) {
    setLastMinutes(minutes)
    setScreen('complete')
  }

  // 再来一段：回到自习页，不换熊
  function handleAgain() {
    setScreen('study')
  }

  if (screen === 'select') {
    return <SelectBear onSelect={handleSelect} onGoStats={() => setScreen('stats')} />
  }

  if (screen === 'study') {
    return (
      <StudyRoom
        bearId={bearId}
        onBack={() => setScreen('select')}
        onFinish={handleFinish}
      />
    )
  }

  if (screen === 'complete') {
    return (
      <Complete
        bearId={bearId}
        minutes={lastMinutes}
        onAgain={handleAgain}
        onGoStats={() => setScreen('stats')}
        onBackHome={() => setScreen('select')}
      />
    )
  }

  return <Stats onBack={() => setScreen('select')} />
}
