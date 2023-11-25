import List from "@/components/List"
import TheFooter from "@/components/TheFooter"
import TheHeader from "@/components/TheHeader"
import Visuals from "@/components/Visuals"

function App() {
  return (
    <div className="h-screen flex flex-col bg-main text-white">
      <TheHeader />
      <main className="flex-1 flex container mx-auto">
        <aside className="flex-1 border">
          <List />
        </aside>
        <section className="flex-[2] border flex">
          <Visuals />
        </section>
      </main>
      <TheFooter />
    </div>
  )
}

export default App
