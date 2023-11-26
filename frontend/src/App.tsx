import List from "@/components/List"
import TheFooter from "@/components/TheFooter"
import TheHeader from "@/components/TheHeader"
import Visuals from "@/components/Visuals"
import Aside from "./components/Aside"
import Search from "./components/Search"

function App() {

  return (
    <div className="min-h-screen flex flex-col bg-main text-white">
      <TheHeader />
      <main className="flex-1 flex flex-col container mx-auto mt-8">
        <div className="flex flex-1">
          <div className="flex">
            <Aside />
          </div>
          <div className="flex-1 flex flex-col">
            <Search />
            <div className="flex flex-1">
              <section className="flex-1"><List /></section>
              <section className="flex flex-1"><Visuals /></section>
            </div>
          </div>
        </div>
      </main>
      <TheFooter />
    </div>
  )
}

export default App
