import List from "@/components/List"
import TheFooter from "@/components/TheFooter"
import TheHeader from "@/components/TheHeader"
import Visuals from "@/components/Visuals"
import Aside from "./components/Aside"

function App() {

  return (
    <div className="min-h-screen flex flex-col bg-main text-white">
      <TheHeader />
      <main className="flex-1 flex flex-col container mx-auto">
        <div className="flex flex-1">
          <div>
            <Aside />
          </div>
          <div className="flex-1 flex flex-col">
            <form action="" className="">
              <input type="text" placeholder="search" />
              <button type="submit">search</button>

            </form>
            <div className="border flex flex-1">
              <section className="border flex-1"><List /></section>
              <section className="flex border flex-1"><Visuals /></section>
            </div>
          </div>
        </div>
      </main>
      <TheFooter />
    </div>
  )
}

export default App
